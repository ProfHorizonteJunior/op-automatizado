"""Verificador de ícones referenciados em arquiteturas YAML.

Percorre todos os serviços de um arquivo de arquitetura e confere se cada
ícone declarado no campo ``icone`` existe fisicamente na pasta de ícones.

Uso direto:
    python arquitetura/verificar_icones.py arquiteturas/<nome>.yaml
    python arquitetura/verificar_icones.py arquiteturas/<nome>.yaml --icones /caminho
    python arquitetura/verificar_icones.py arquiteturas/   # verifica todos os YAMLs
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ICONES_PADRAO = RAIZ / "icones"


# ── Tipos de problema ─────────────────────────────────────────────────────────

@dataclass
class CampoIconeAusente:
    """Serviço que não declarou o campo ``icone``."""
    servico_id: str
    servico_nome: str

    def __str__(self) -> str:
        return (
            f"[{self.servico_id}] {self.servico_nome!r} "
            "→ campo 'icone' não declarado"
        )


@dataclass
class ArquivoIconeNaoEncontrado:
    """Serviço cujo arquivo SVG não existe na pasta de ícones."""
    servico_id: str
    servico_nome: str
    icone: str

    def __str__(self) -> str:
        return (
            f"[{self.servico_id}] {self.servico_nome!r} "
            f"→ arquivo não encontrado: '{self.icone}'"
        )


# ── Resultado ─────────────────────────────────────────────────────────────────

@dataclass
class ResultadoVerificacao:
    """Resultado da verificação de ícones de um único arquivo YAML."""
    arquivo: Path
    total_servicos: int
    sem_campo: list[CampoIconeAusente] = field(default_factory=list)
    ausentes: list[ArquivoIconeNaoEncontrado] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True quando não há nenhum problema."""
        return not self.sem_campo and not self.ausentes

    @property
    def total_erros(self) -> int:
        return len(self.sem_campo) + len(self.ausentes)

    @property
    def problemas(self) -> list:
        """Lista unificada de todos os problemas encontrados."""
        return [*self.sem_campo, *self.ausentes]


# ── Lógica principal ──────────────────────────────────────────────────────────

def verificar_icones(
    caminho_yaml: str | Path,
    pasta_icones: str | Path = PASTA_ICONES_PADRAO,
) -> ResultadoVerificacao:
    """Verifica se todos os ícones declarados no YAML existem em *pasta_icones*.

    Parameters
    ----------
    caminho_yaml:
        Caminho para o arquivo de arquitetura ``.yaml``.
    pasta_icones:
        Pasta onde os arquivos SVG dos ícones devem estar.

    Returns
    -------
    ResultadoVerificacao
        Objeto com listas de problemas e flag ``ok``.

    Raises
    ------
    FileNotFoundError
        Se *caminho_yaml* não existir.
    yaml.YAMLError
        Se o conteúdo do arquivo não for YAML válido.
    """
    caminho_yaml = Path(caminho_yaml)
    pasta_icones = Path(pasta_icones)

    with open(caminho_yaml, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    servicos = (doc or {}).get("servicos") or []
    resultado = ResultadoVerificacao(
        arquivo=caminho_yaml,
        total_servicos=len(servicos),
    )

    for servico in servicos:
        sid = servico.get("id", "?")
        snome = servico.get("nome", "?")
        icone = servico.get("icone")

        if not icone:
            resultado.sem_campo.append(CampoIconeAusente(sid, snome))
        elif not (pasta_icones / icone).is_file():
            resultado.ausentes.append(
                ArquivoIconeNaoEncontrado(sid, snome, icone)
            )

    return resultado


def verificar_diretorio(
    pasta_yaml: str | Path,
    pasta_icones: str | Path = PASTA_ICONES_PADRAO,
) -> list[ResultadoVerificacao]:
    """Verifica todos os ``.yaml`` encontrados em *pasta_yaml*."""
    pasta_yaml = Path(pasta_yaml)
    return [
        verificar_icones(arq, pasta_icones)
        for arq in sorted(pasta_yaml.glob("*.yaml"))
    ]


# ── CLI ───────────────────────────────────────────────────────────────────────

def _formatar_resultado(res: ResultadoVerificacao) -> str:
    """Retorna string formatada do resultado de um arquivo."""
    linhas: list[str] = []
    nome = res.arquivo.name
    if res.ok:
        linhas.append(
            f"  ✓  {nome} — {res.total_servicos} serviço(s), ícones OK"
        )
    else:
        linhas.append(
            f"  ✗  {nome} — {res.total_erros} problema(s) "
            f"em {res.total_servicos} serviço(s):"
        )
        for problema in res.problemas:
            linhas.append(f"       • {problema}")
    return "\n".join(linhas)


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada da CLI.

    Returns
    -------
    int
        0 se todos os ícones foram encontrados, 1 caso contrário.
    """
    parser = argparse.ArgumentParser(
        description="Verifica se os ícones referenciados em arquiteturas YAML existem.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python arquitetura/verificar_icones.py arquiteturas/site-estatico.yaml\n"
            "  python arquitetura/verificar_icones.py arquiteturas/\n"
            "  python arquitetura/verificar_icones.py arquiteturas/ --icones /tmp/icons\n"
        ),
    )
    parser.add_argument(
        "alvo",
        help="Arquivo .yaml ou pasta contendo múltiplos .yaml.",
    )
    parser.add_argument(
        "--icones",
        default=PASTA_ICONES_PADRAO,
        help=f"Pasta de ícones SVG (padrão: {PASTA_ICONES_PADRAO})",
    )
    args = parser.parse_args(argv)

    alvo = Path(args.alvo)
    pasta_icones = Path(args.icones)

    if not pasta_icones.is_dir():
        print(f"ERRO: pasta de ícones não encontrada: {pasta_icones}")
        return 1

    if alvo.is_dir():
        resultados = verificar_diretorio(alvo, pasta_icones)
        if not resultados:
            print(f"Nenhum .yaml encontrado em '{alvo}'.")
            return 0
    elif alvo.is_file():
        resultados = [verificar_icones(alvo, pasta_icones)]
    else:
        print(f"ERRO: '{alvo}' não é um arquivo nem uma pasta válida.")
        return 1

    print(f"\nVerificação de ícones — pasta: {pasta_icones}\n")
    for res in resultados:
        print(_formatar_resultado(res))

    total_erros = sum(r.total_erros for r in resultados)
    total_servicos = sum(r.total_servicos for r in resultados)
    print(
        f"\nResumo: {len(resultados)} arquivo(s) | "
        f"{total_servicos} serviço(s) verificado(s) | "
        f"{total_erros} problema(s)."
    )
    return 1 if total_erros else 0


if __name__ == "__main__":
    sys.exit(main())
