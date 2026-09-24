"""Renderiza uma arquitetura YAML em SVG (layout em grade, esquerda para direita).

Uso:
    python renderizador/renderizar.py arquiteturas/<nome>.yaml [--saida saida]
    python renderizador/renderizar.py arquiteturas/<nome>.yaml --icones /caminho/icones
"""
import argparse
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

RAIZ = Path(__file__).resolve().parent.parent

# ── Constantes visuais ────────────────────────────────────────────────────────
TAMANHO_ICONE = 64          # px — largura/altura do ícone SVG
ESPACAMENTO_H = 160         # px — espaço horizontal entre centros de coluna
ESPACAMENTO_V = 140         # px — espaço vertical entre centros de linha
MARGEM = 60                 # px — margem externa do canvas
LABEL_OFFSET_Y = 22         # px — distância do texto abaixo do ícone
FONT_SIZE_TITULO = 14
FONT_SIZE_LABEL = 11
FONT_SIZE_NUMERO = 10
COR_BORDA = "#232F3E"
COR_SETA = "#545B64"
MAX_COLUNAS = 4             # número máximo de nós por linha na grade


def _colunas_linhas(n: int, max_colunas: int) -> tuple[int, int]:
    """Retorna (colunas, linhas) para encaixar *n* nós na grade."""
    colunas = min(n, max_colunas)
    linhas = math.ceil(n / colunas) if colunas else 1
    return colunas, linhas


def _posicoes(servicos: list[dict], max_colunas: int) -> dict[str, tuple[float, float]]:
    """Calcula o centro (cx, cy) de cada serviço na grade."""
    colunas, _ = _colunas_linhas(len(servicos), max_colunas)
    pos: dict[str, tuple[float, float]] = {}
    for i, servico in enumerate(servicos):
        col = i % colunas
        linha = i // colunas
        cx = MARGEM + TAMANHO_ICONE / 2 + col * ESPACAMENTO_H
        cy = MARGEM + 40 + TAMANHO_ICONE / 2 + linha * ESPACAMENTO_V
        pos[servico["id"]] = (cx, cy)
    return pos


def _canvas(posicoes: dict[str, tuple[float, float]]) -> tuple[float, float]:
    """Calcula largura e altura mínima para conter todos os nós com margem."""
    if not posicoes:
        return MARGEM * 2, MARGEM * 2
    max_cx = max(cx for cx, _ in posicoes.values())
    max_cy = max(cy for _, cy in posicoes.values())
    largura = max_cx + TAMANHO_ICONE / 2 + MARGEM
    altura = max_cy + TAMANHO_ICONE / 2 + LABEL_OFFSET_Y + 20 + MARGEM
    return largura, altura


def _seta(x1: float, y1: float, x2: float, y2: float, numero: int) -> list[str]:
    """Gera a linha com seta e o rótulo numérico entre dois centros de ícone.

    Ajusta os pontos de início/fim para partir da borda do ícone, não do centro,
    e garante que a seta aponta sempre na direção correta (inclusive para a esquerda).
    """
    meio = TAMANHO_ICONE / 2
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy) or 1

    # Recua cada extremidade até a borda do ícone (círculo de raio = meio)
    px1 = x1 + dx / dist * (meio + 4)
    py1 = y1 + dy / dist * (meio + 4)
    px2 = x2 - dx / dist * (meio + 4)
    py2 = y2 - dy / dist * (meio + 4)

    # Rótulo numérico perpendicular à linha, deslocado 14px
    perp_x = -dy / dist * 14
    perp_y = dx / dist * 14
    lx = (px1 + px2) / 2 + perp_x
    ly = (py1 + py2) / 2 + perp_y

    return [
        f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" '
        f'stroke="{COR_SETA}" stroke-width="1.5" marker-end="url(#seta)"/>',
        f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{FONT_SIZE_NUMERO}" '
        f'text-anchor="middle" fill="{COR_SETA}">{numero}</text>',
    ]


def _icone_elemento(servico: dict, cx: float, cy: float, pasta_icones: Path) -> list[str]:
    """Gera os elementos SVG de ícone + label para um serviço.

    Se o arquivo SVG não existir, renderiza um retângulo cinza como placeholder
    em vez de uma imagem invisível.
    """
    x = cx - TAMANHO_ICONE / 2
    y = cy - TAMANHO_ICONE / 2
    texto_y = cy + TAMANHO_ICONE / 2 + LABEL_OFFSET_Y
    label = escape(servico.get("nome", servico.get("id", "?")))

    icone = servico.get("icone", "")
    caminho_icone = (pasta_icones / icone).resolve() if icone else None

    if caminho_icone and caminho_icone.is_file():
        img = (
            f'<image href="{caminho_icone.as_uri()}" '
            f'x="{x:.1f}" y="{y:.1f}" '
            f'width="{TAMANHO_ICONE}" height="{TAMANHO_ICONE}"/>'
        )
    else:
        # Placeholder visual quando o ícone não está disponível
        img = (
            f'<rect x="{x:.1f}" y="{y:.1f}" '
            f'width="{TAMANHO_ICONE}" height="{TAMANHO_ICONE}" '
            f'fill="#e8e8e8" stroke="#aaa" stroke-width="1" rx="6"/>'
            f'<text x="{cx:.1f}" y="{cy + 4:.1f}" font-size="9" '
            f'text-anchor="middle" fill="#888">{escape(icone or "?")}</text>'
        )

    rotulo = (
        f'<text x="{cx:.1f}" y="{texto_y:.1f}" '
        f'font-size="{FONT_SIZE_LABEL}" text-anchor="middle">{label}</text>'
    )
    return [img, rotulo]


def renderizar_svg(doc: dict, pasta_icones: str | Path) -> str:
    """Converte um documento de arquitetura YAML em SVG.

    Parameters
    ----------
    doc:
        Dicionário já carregado do YAML de arquitetura.
    pasta_icones:
        Pasta onde estão os arquivos ``.svg`` dos ícones.

    Returns
    -------
    str
        Conteúdo SVG completo como string.
    """
    pasta_icones = Path(pasta_icones)
    servicos: list[dict] = doc.get("servicos") or []
    conexoes: list[dict] = doc.get("conexoes") or []

    posicoes = _posicoes(servicos, MAX_COLUNAS)
    largura, altura = _canvas(posicoes)

    partes: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{largura:.0f}" height="{altura:.0f}" '
        f'font-family="Arial, sans-serif">',
        # Marcador de seta reutilizável
        '<defs>'
        '<marker id="seta" markerWidth="10" markerHeight="10" '
        'refX="9" refY="3" orient="auto">'
        '<path d="M0,0 L9,3 L0,6 z" fill="{cor}"/>'
        "</marker>"
        "</defs>".format(cor=COR_SETA),
        # Borda do diagrama
        f'<rect x="10" y="10" width="{largura - 20:.0f}" height="{altura - 20:.0f}" '
        f'fill="none" stroke="{COR_BORDA}" stroke-width="2"/>',
        # Título
        f'<text x="20" y="32" font-size="{FONT_SIZE_TITULO}" fill="{COR_BORDA}">'
        f'{escape(doc.get("nome", ""))}</text>',
    ]

    # Conexões (desenhadas antes dos ícones para ficar sob eles)
    for n, conexao in enumerate(conexoes, start=1):
        origem = conexao.get("de")
        destino = conexao.get("para")
        if origem not in posicoes or destino not in posicoes:
            continue  # conexão inválida — ignorada silenciosamente na renderização
        x1, y1 = posicoes[origem]
        x2, y2 = posicoes[destino]
        partes.extend(_seta(x1, y1, x2, y2, n))

    # Ícones e labels (desenhados sobre as linhas)
    for servico in servicos:
        sid = servico.get("id")
        if sid not in posicoes:
            continue
        cx, cy = posicoes[sid]
        partes.extend(_icone_elemento(servico, cx, cy, pasta_icones))

    partes.append("</svg>")
    return "\n".join(partes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Renderiza arquitetura YAML em SVG.")
    parser.add_argument("arquivo", help="Caminho para o arquivo .yaml de arquitetura.")
    parser.add_argument(
        "--icones",
        default=str(RAIZ / "icones"),
        help="Pasta de ícones SVG (padrão: icones/).",
    )
    parser.add_argument(
        "--saida",
        default=str(RAIZ / "saida"),
        help="Pasta de destino do SVG gerado (padrão: saida/).",
    )
    args = parser.parse_args(argv)

    with open(args.arquivo, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    destino = Path(args.saida) / f"{Path(args.arquivo).stem}.svg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(renderizar_svg(doc, args.icones), encoding="utf-8")
    print(f"Diagrama salvo em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
