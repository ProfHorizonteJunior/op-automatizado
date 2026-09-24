# Requisitos — Validador de Arquitetura

## Requisito 1 — Estrutura do YAML
**História:** Como aluno, quero que o validador verifique o YAML da arquitetura, para detectar erros antes da renderização.

### Critérios de aceitação
1. QUANDO o arquivo não for YAML válido, O validador DEVE informar a linha do erro.
2. QUANDO faltar um campo obrigatório (`nome`, `servicos`, `conexoes`), O validador DEVE listar os campos ausentes.

## Requisito 2 — Serviços e ícones
**História:** Como aluno, quero garantir que cada serviço tenha um ícone oficial.

### Critérios de aceitação
1. QUANDO um serviço não tiver ícone correspondente em `icones/`, O validador DEVE reportar o serviço.

## Requisito 3 — Conexões
### Critérios de aceitação
1. QUANDO uma conexão referenciar um serviço inexistente, O validador DEVE reportar a conexão inválida.
2. QUANDO tudo estiver correto, O validador DEVE retornar código de saída 0.
