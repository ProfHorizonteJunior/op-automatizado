"""Validador de arquiteturas AWS descritas em YAML.

Uso:
    python arquitetura/validador.py arquiteturas/<nome>.yaml [--icones icones]
"""
import argparse
import sys
from pathlib import Path

import yaml

CAMPOS_OBRIGATORIOS = ("nome", "servicos", "conexoes")
PASTA_ICONES_PADRAO = Path(__file__).resolve().parent.parent / "icones"


class ErroYaml(Exception):
    pass


def carregar_yaml(caminho):
    """Lê e faz parse do arquivo. Levanta ErroYaml com a linha do erro."""
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return yaml.safe_load(arquivo)
    except yaml.YAMLError as erro:
        marca = getattr(erro, "problem_mark", None)
        linha = f" (linha {marca.line + 1})" if marca else ""
        raise ErroYaml(f"YAML inválido{linha}: {erro}") from erro


def validar_campos(doc):
    if not isinstance(doc, dict):
        return ["Documento vazio ou não é um mapeamento YAML."]
    ausentes = [campo for campo in CAMPOS_OBRIGATORIOS if not doc.get(campo)]
    if ausentes:
        return [f"Campos obrigatórios ausentes: {', '.join(ausentes)}"]
    return []


def validar_icones(doc, pasta_icones):
    erros = []
    pasta = Path(pasta_icones)
    for servico in doc.get("servicos") or []:
        ident = servico.get("id", "?")
        icone = servico.get("icone")
        if not icone:
            erros.append(f"Serviço '{ident}' sem campo 'icone'.")
        elif not (pasta / icone).is_file():
            erros.append(f"Serviço '{ident}': ícone '{icone}' não encontrado em {pasta}.")
    return erros


def validar_conexoes(doc):
    ids = {servico.get("id") for servico in doc.get("servicos") or []}
    erros = []
    for i, conexao in enumerate(doc.get("conexoes") or [], start=1):
        for lado in ("de", "para"):
            alvo = conexao.get(lado)
            if alvo not in ids:
                erros.append(f"Conexão {i}: '{lado}' referencia serviço inexistente '{alvo}'.")
    return erros


def validar(caminho, pasta_icones=PASTA_ICONES_PADRAO):
    try:
        doc = carregar_yaml(caminho)
    except ErroYaml as erro:
        return [str(erro)]
    erros = validar_campos(doc)
    if erros:
        return erros
    return validar_icones(doc, pasta_icones) + validar_conexoes(doc)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Valida arquitetura AWS em YAML.")
    parser.add_argument("arquivo")
    parser.add_argument("--icones", default=PASTA_ICONES_PADRAO)
    args = parser.parse_args(argv)

    erros = validar(args.arquivo, args.icones)
    if erros:
        for erro in erros:
            print(f"ERRO: {erro}")
        return 1
    print(f"OK: {args.arquivo} é válido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
