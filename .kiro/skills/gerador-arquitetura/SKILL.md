---
name: gerador-arquitetura
description: Gera um diagrama de arquitetura AWS a partir de um caso de uso descrito em casos/. Use quando o usuário pedir para criar ou atualizar uma arquitetura.
---

# Gerador de Arquitetura

## Fluxo
1. Ler o caso de uso em `casos/<nome>/caso.yaml`.
2. Escolher os serviços AWS adequados, seguindo `.kiro/steering/guia-visual-aws.md`.
3. Escrever a arquitetura em `arquiteturas/<nome>.yaml`.
4. Validar com `python arquitetura/validador.py arquiteturas/<nome>.yaml`.
5. Renderizar com o `renderizador/`, salvando o resultado em `saida/`.

## Regras
- Consultar a documentação oficial via MCP (`aws-docs`) antes de escolher serviços.
- Não prosseguir para a renderização se a validação falhar.
