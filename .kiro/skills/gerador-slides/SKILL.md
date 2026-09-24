---
name: gerador-slides
description: Gera slides de apresentação a partir de uma arquitetura já renderizada em saida/. Use quando o usuário pedir slides ou apresentação da arquitetura (atividade da tarde).
---

# Gerador de Slides

## Fluxo
1. Ler a arquitetura em `arquiteturas/<nome>.yaml` e o diagrama em `saida/`.
2. Montar a apresentação em `slides/<nome>/`:
   - Slide 1: título e problema (do caso de uso).
   - Slide 2: diagrama da arquitetura.
   - Slide 3+: um slide por serviço principal, explicando seu papel.
   - Último slide: custos, riscos e próximos passos.
3. Seguir o `.kiro/steering/guia-visual-aws.md` para nomes e ícones.
