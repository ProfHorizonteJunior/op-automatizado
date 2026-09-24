# Design — Validador de Arquitetura

## Visão geral
Script `arquitetura/validador.py` executado por linha de comando:

```bash
python arquitetura/validador.py arquiteturas/<nome>.yaml
```

## Componentes
- `carregar_yaml(caminho)` — lê e faz parse do arquivo.
- `validar_campos(doc)` — verifica campos obrigatórios.
- `validar_icones(doc, pasta_icones)` — confere ícones em `icones/`.
- `validar_conexoes(doc)` — confere origem/destino das conexões.

## Saída
- Lista de erros no terminal.
- Código de saída `0` (válido) ou `1` (inválido).

## Testes
- Casos em `tests/`, usando `pytest`.
