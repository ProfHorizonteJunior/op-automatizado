import textwrap

import pytest

from arquitetura.validador import main, validar


@pytest.fixture
def icones(tmp_path):
    pasta = tmp_path / "icones"
    pasta.mkdir()
    (pasta / "S3.svg").write_text("<svg/>")
    (pasta / "Lambda.svg").write_text("<svg/>")
    return pasta


def escrever(tmp_path, conteudo):
    arquivo = tmp_path / "arq.yaml"
    arquivo.write_text(textwrap.dedent(conteudo), encoding="utf-8")
    return arquivo


VALIDO = """
    nome: teste
    servicos:
      - {id: fn, nome: AWS Lambda, icone: Lambda.svg}
      - {id: s3, nome: Amazon S3, icone: S3.svg}
    conexoes:
      - {de: fn, para: s3}
"""


def test_yaml_invalido_informa_linha(tmp_path, icones):
    arquivo = escrever(tmp_path, "nome: x\nservicos: [\n")
    erros = validar(arquivo, icones)
    assert "linha" in erros[0]


def test_campos_ausentes(tmp_path, icones):
    arquivo = escrever(tmp_path, "nome: x\n")
    erros = validar(arquivo, icones)
    assert "servicos" in erros[0] and "conexoes" in erros[0]


def test_icone_inexistente(tmp_path, icones):
    arquivo = escrever(tmp_path, VALIDO.replace("S3.svg", "Nao.svg"))
    erros = validar(arquivo, icones)
    assert any("'s3'" in erro for erro in erros)


def test_conexao_invalida(tmp_path, icones):
    arquivo = escrever(tmp_path, VALIDO.replace("para: s3", "para: rds"))
    erros = validar(arquivo, icones)
    assert any("rds" in erro for erro in erros)


def test_valido_retorna_zero(tmp_path, icones):
    arquivo = escrever(tmp_path, VALIDO)
    assert main([str(arquivo), "--icones", str(icones)]) == 0


def test_invalido_retorna_um(tmp_path, icones):
    arquivo = escrever(tmp_path, "nome: x\n")
    assert main([str(arquivo), "--icones", str(icones)]) == 1
