"""Renderiza uma arquitetura YAML em SVG (fluxo da esquerda para a direita).

Uso:
    python renderizador/renderizar.py arquiteturas/<nome>.yaml [--saida saida]
"""
import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

RAIZ = Path(__file__).resolve().parent.parent
LARGURA_COLUNA = 200
TAMANHO_ICONE = 64
MARGEM = 60
COR_AWS_CLOUD = "#232F3E"


def renderizar_svg(doc, pasta_icones):
    servicos = doc["servicos"]
    posicoes = {}
    for i, servico in enumerate(servicos):
        x = MARGEM + i * LARGURA_COLUNA
        posicoes[servico["id"]] = (x, MARGEM + 40)

    largura = MARGEM * 2 + LARGURA_COLUNA * (len(servicos) - 1) + TAMANHO_ICONE
    altura = MARGEM * 2 + 40 + TAMANHO_ICONE + 40

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'font-family="Arial, sans-serif">',
        '<defs><marker id="seta" markerWidth="10" markerHeight="10" refX="9" refY="3" '
        'orient="auto"><path d="M0,0 L9,3 L0,6 z" fill="#545B64"/></marker></defs>',
        f'<rect x="10" y="10" width="{largura - 20}" height="{altura - 20}" fill="none" '
        f'stroke="{COR_AWS_CLOUD}" stroke-width="2"/>',
        f'<text x="20" y="32" font-size="14" fill="{COR_AWS_CLOUD}">'
        f'{escape(doc.get("nome", ""))}</text>',
    ]

    for n, conexao in enumerate(doc["conexoes"], start=1):
        x1, y1 = posicoes[conexao["de"]]
        x2, y2 = posicoes[conexao["para"]]
        meio = TAMANHO_ICONE / 2
        partes.append(
            f'<line x1="{x1 + TAMANHO_ICONE + 8}" y1="{y1 + meio}" x2="{x2 - 8}" '
            f'y2="{y2 + meio}" stroke="#545B64" stroke-width="2" marker-end="url(#seta)"/>'
        )
        partes.append(
            f'<text x="{(x1 + x2 + TAMANHO_ICONE) / 2}" y="{y1 + meio - 8}" font-size="12" '
            f'text-anchor="middle" fill="#545B64">{n}</text>'
        )

    for servico in servicos:
        x, y = posicoes[servico["id"]]
        icone = (Path(pasta_icones) / servico["icone"]).resolve()
        partes.append(
            f'<image href="{icone.as_uri()}" x="{x}" y="{y}" '
            f'width="{TAMANHO_ICONE}" height="{TAMANHO_ICONE}"/>'
        )
        partes.append(
            f'<text x="{x + TAMANHO_ICONE / 2}" y="{y + TAMANHO_ICONE + 20}" font-size="12" '
            f'text-anchor="middle">{escape(servico["nome"])}</text>'
        )

    partes.append("</svg>")
    return "\n".join(partes)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Renderiza arquitetura YAML em SVG.")
    parser.add_argument("arquivo")
    parser.add_argument("--icones", default=RAIZ / "icones")
    parser.add_argument("--saida", default=RAIZ / "saida")
    args = parser.parse_args(argv)

    with open(args.arquivo, encoding="utf-8") as arquivo:
        doc = yaml.safe_load(arquivo)

    destino = Path(args.saida) / f"{Path(args.arquivo).stem}.svg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(renderizar_svg(doc, args.icones), encoding="utf-8")
    print(f"Diagrama salvo em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
