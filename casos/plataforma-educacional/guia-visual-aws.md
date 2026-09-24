# Guia Visual AWS — Plataforma Educacional

Este guia mapeia cada componente do diagrama de arquitetura ao serviço AWS
correspondente, explica o papel de cada ícone e orienta quais SVGs baixar do
[AWS Architecture Icons](https://aws.amazon.com/architecture/icons/).

---

## Como baixar os ícones

1. Acesse https://aws.amazon.com/architecture/icons/
2. Baixe o pacote **"AWS Architecture Icons (SVG)"**
3. Copie os arquivos listados abaixo para a pasta `icones/` do repositório

---

## Mapa de ícones por serviço

| Serviço no YAML | Ícone esperado (`icones/`) | Categoria no pacote AWS |
|---|---|---|
| Estudante | `Users.svg` | General / Users |
| Professor (Admin) | `User.svg` | General / User |
| Frontend Web | `Client.svg` | General / Client |
| API Gateway | `Amazon-API-Gateway.svg` | Networking & Content Delivery |
| Serviço de Autenticação | `Amazon-Cognito.svg` | Security, Identity & Compliance |
| Serviço de Turmas | `AWS-Organizations.svg` | Management & Governance |
| Serviço de UCs | `Amazon-S3.svg` | Storage |
| Serviço do Agente IA | `Amazon-Bedrock.svg` | Machine Learning |
| Serviço de Chamados | `Amazon-SQS.svg` | Application Integration |
| Serviço de Moedas | `AWS-Cost-Explorer.svg` | Cloud Financial Management |
| Serviço de Anotações | `Amazon-DocumentDB.svg` | Database |
| Serviço Administrativo | `AWS-Management-Console.svg` | Management & Governance |
| Agendador (Cron) | `Amazon-EventBridge.svg` | Application Integration |
| Banco de Dados Relacional | `Amazon-RDS.svg` | Database |
| Armazenamento de PDFs | `Amazon-Simple-Storage-Service.svg` | Storage |
| Base Vetorial (RAG) | `Amazon-OpenSearch-Service.svg` | Analytics |

---

## Papel de cada serviço na arquitetura

### Amazon Cognito
Gerencia o cadastro e login de estudantes e professores. Emite tokens JWT
usados em todas as chamadas autenticadas à API. Perfis distintos (`estudante`
e `professor`) controlam o acesso às rotas.

### Amazon API Gateway
Ponto de entrada único para o frontend. Roteia cada requisição ao Lambda
handler correto, aplica throttling e valida o token Cognito antes de
encaminhar.

### Amazon Bedrock
Executa o modelo de linguagem (Claude 3) com o contexto dos PDFs da UC ativa.
Os **Bedrock Guardrails** bloqueiam automaticamente respostas que contenham
código-fonte completo, garantindo que o agente apenas oriente o aluno.

### Amazon OpenSearch Service (Serverless)
Armazena os vetores gerados a partir dos PDFs de cada UC. O agente realiza
buscas semânticas para recuperar os trechos mais relevantes antes de montar
a resposta ao aluno (RAG — Retrieval-Augmented Generation).

### Amazon S3 (`Amazon-Simple-Storage-Service.svg`)
Bucket dedicado ao upload dos PDFs pelo professor. O upload é feito via
presigned URL gerada pela API, sem trafegar o arquivo pelo servidor.

### Amazon RDS (PostgreSQL)
Banco de dados relacional principal. Armazena usuários, turmas, UCs, chamados,
atribuições, moedas, anotações e histórico de chat. Configurado com Multi-AZ
em produção para alta disponibilidade.

### Amazon SQS *(representação do Serviço de Chamados)*
Ilustra o fluxo assíncrono de chamados: criação → atribuição → resolução →
validação. Em produção, uma fila SQS pode ser usada para desacoplar o
disparo de eventos de expiração do timer de 4h.

### Amazon EventBridge Scheduler
Executa o job periódico (a cada 15 min) que verifica chamados com timer
expirado e os devolve automaticamente à fila de abertos, sem necessidade de
polling no frontend.

### Amazon DocumentDB *(representação do Serviço de Anotações)*
Ícone usado para representar o serviço de anotações do professor. Em
implementação real, as anotações são armazenadas no RDS PostgreSQL (campo
JSONB para blocos de conteúdo rico).

### AWS Organizations *(representação do Serviço de Turmas)*
Representa visualmente a gestão hierárquica de grupos (turmas → alunos),
análoga à estrutura de contas do AWS Organizations.

### Amazon Cognito *(Auth)*
Ver seção acima.

---

## Fluxo resumido do diagrama

```
Estudante / Professor
       │
       ▼
  Frontend (Next.js)
       │
       ▼
  API Gateway  ──► Cognito (auth)
       │
       ├──► Serviço Turmas     ──► RDS
       ├──► Serviço UCs        ──► RDS + S3 + OpenSearch
       ├──► Serviço Agente IA  ──► RDS + OpenSearch + Bedrock
       ├──► Serviço Chamados   ──► RDS ──► Serviço Moedas
       ├──► Serviço Moedas     ──► RDS
       ├──► Serviço Anotações  ──► RDS
       └──► Serviço Admin      ──► RDS

  EventBridge Scheduler ──► Serviço Chamados (expiração 4h)
```

---

## Checklist antes de renderizar

- [ ] Todos os SVGs listados na tabela acima estão em `icones/`
- [ ] Rode o validador: `python arquitetura/validador.py arquiteturas/plataforma-educacional.yaml`
- [ ] Nenhum erro de ícone ausente ou conexão inválida reportado
- [ ] Execute o renderizador: `python renderizador/renderizar.py arquiteturas/plataforma-educacional.yaml`
- [ ] Abra `saida/plataforma-educacional.svg` e confirme o diagrama visualmente
