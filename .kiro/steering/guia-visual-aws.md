---
inclusion: always
---

# Guia Visual AWS

Contexto que o agente sempre lê ao gerar diagramas de arquitetura.

## Ícones
- Use somente os ícones oficiais da pasta `icones/` (AWS Architecture Icons).
- Não invente ícones nem use logos de terceiros.
- Rótulo abaixo de cada ícone com o nome oficial do serviço (ex.: "Amazon S3", "AWS Lambda").

## Agrupamentos
- `AWS Cloud` → `Region` → `VPC` → `Availability Zone` → `Subnet (pública/privada)`.
- Cores dos grupos seguem o padrão oficial AWS:
  - AWS Cloud: `#232F3E`
  - Region: `#00A4A6` (tracejado)
  - VPC: `#8C4FFF`
  - Subnet pública: `#7AA116`
  - Subnet privada: `#00A4A6`

## Fluxo
- Setas da esquerda para a direita (usuário → borda → aplicação → dados).
- Setas numeradas quando a ordem do fluxo importar.

## Saída
- Arquiteturas descritas em YAML em `arquiteturas/`.
- Renderização feita por `renderizador/`, resultado em `saida/`.
