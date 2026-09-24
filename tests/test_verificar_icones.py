"""Testes para arquitetura/verificar_icones.py."""
import textwrap

import pytest

from arquitetura.verificar_icones import (
    ArquivoIconeNaoEncontrado,
    CampoIconeAusente,
    ResultadoVerificacao,
    main,
    verificar_diretorio,
    verificar_icones,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def icones(tmp_path):
    """Pasta de ícones com dois SVGs de exemplo."""
    pasta = tmp_path / "icones"
    pasta.mkdir()
    (pasta / "Bedrock.svg").write_text("<svg/>")
    (pasta / "S3.svg").write_text("<svg/>")
    (pasta / "RDS.svg").write_text("<svg/>")
    return pasta


def escrever_yaml(tmp_path, conteudo: str, nome: str = "arq.yaml"):
    """Escreve um YAML no tmp_path e retorna o caminho."""
    arquivo = tmp_path / nome
    arquivo.write_text(textwrap.dedent(conteudo), encoding="utf-8")
    return arquivo


YAML_VALIDO = """
    nome: teste
    servicos:
      - {id: ia, nome: Agente IA, icone: Bedrock.svg}
      - {id: s3, nome: Storage, icone: S3.svg}
      - {id: db, nome: Banco, icone: RDS.svg}
    conexoes:
      - {de: ia, para: s3}
      - {de: ia, para: db}
"""

YAML_ICONE_AUSENTE = """
    nome: teste
    servicos:
      - {id: ia, nome: Agente IA, icone: Bedrock.svg}
      - {id: s3, nome: Storage, icone: Inexistente.svg}
    conexoes:
      - {de: ia, para: s3}
"""

YAML_SEM_CAMPO_ICONE = """
    nome: teste
    servicos:
      - {id: ia, nome: Agente IA, icone: Bedrock.svg}
      - {id: s3, nome: Storage}
    conexoes:
      - {de: ia, para: s3}
"""

YAML_MULTIPLOS_ERROS = """
    nome: teste
    servicos:
      - {id: ia, nome: Agente IA}
      - {id: s3, nome: Storage, icone: Nao.svg}
      - {id: db, nome: Banco, icone: Tambem-nao.svg}
    conexoes: []
"""


# ── Testes de verificar_icones ────────────────────────────────────────────────

class TestVerificarIcones:
    def test_todos_icones_presentes_retorna_ok(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_VALIDO)
        resultado = verificar_icones(arquivo, icones)

        assert resultado.ok is True
        assert resultado.total_erros == 0
        assert resultado.total_servicos == 3

    def test_icone_ausente_detectado(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_ICONE_AUSENTE)
        resultado = verificar_icones(arquivo, icones)

        assert resultado.ok is False
        assert len(resultado.ausentes) == 1
        assert isinstance(resultado.ausentes[0], ArquivoIconeNaoEncontrado)
        assert resultado.ausentes[0].servico_id == "s3"
        assert resultado.ausentes[0].icone == "Inexistente.svg"

    def test_campo_icone_ausente_detectado(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_SEM_CAMPO_ICONE)
        resultado = verificar_icones(arquivo, icones)

        assert resultado.ok is False
        assert len(resultado.sem_campo) == 1
        assert isinstance(resultado.sem_campo[0], CampoIconeAusente)
        assert resultado.sem_campo[0].servico_id == "s3"

    def test_multiplos_erros_contados_corretamente(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_MULTIPLOS_ERROS)
        resultado = verificar_icones(arquivo, icones)

        assert resultado.ok is False
        assert resultado.total_erros == 3  # 1 sem campo + 2 arquivos ausentes
        assert len(resultado.sem_campo) == 1
        assert len(resultado.ausentes) == 2

    def test_propriedade_problemas_unifica_listas(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_MULTIPLOS_ERROS)
        resultado = verificar_icones(arquivo, icones)

        assert len(resultado.problemas) == resultado.total_erros

    def test_resultado_armazena_caminho_do_arquivo(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_VALIDO)
        resultado = verificar_icones(arquivo, icones)

        assert resultado.arquivo == arquivo

    def test_yaml_sem_servicos_retorna_ok(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, "nome: vazio\nservicos: []\nconexoes: []\n")
        resultado = verificar_icones(arquivo, icones)

        assert resultado.ok is True
        assert resultado.total_servicos == 0

    def test_str_de_campo_icone_ausente_contem_id(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_SEM_CAMPO_ICONE)
        resultado = verificar_icones(arquivo, icones)

        assert "s3" in str(resultado.sem_campo[0])

    def test_str_de_arquivo_icone_nao_encontrado_contem_nome_arquivo(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_ICONE_AUSENTE)
        resultado = verificar_icones(arquivo, icones)

        assert "Inexistente.svg" in str(resultado.ausentes[0])


# ── Testes de verificar_diretorio ─────────────────────────────────────────────

class TestVerificarDiretorio:
    def test_verifica_todos_yamls_na_pasta(self, tmp_path, icones):
        escrever_yaml(tmp_path, YAML_VALIDO, "a.yaml")
        escrever_yaml(tmp_path, YAML_ICONE_AUSENTE, "b.yaml")

        resultados = verificar_diretorio(tmp_path, icones)

        assert len(resultados) == 2

    def test_pasta_vazia_retorna_lista_vazia(self, tmp_path, icones):
        resultados = verificar_diretorio(tmp_path, icones)
        assert resultados == []

    def test_ignora_arquivos_nao_yaml(self, tmp_path, icones):
        escrever_yaml(tmp_path, YAML_VALIDO, "valido.yaml")
        (tmp_path / "notas.txt").write_text("ignore me")

        resultados = verificar_diretorio(tmp_path, icones)

        assert len(resultados) == 1

    def test_resultados_ordenados_por_nome(self, tmp_path, icones):
        escrever_yaml(tmp_path, YAML_VALIDO, "z_ultimo.yaml")
        escrever_yaml(tmp_path, YAML_VALIDO, "a_primeiro.yaml")

        resultados = verificar_diretorio(tmp_path, icones)

        assert resultados[0].arquivo.name == "a_primeiro.yaml"
        assert resultados[1].arquivo.name == "z_ultimo.yaml"


# ── Testes da CLI (main) ──────────────────────────────────────────────────────

class TestMain:
    def test_arquivo_valido_retorna_zero(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_VALIDO)
        assert main([str(arquivo), "--icones", str(icones)]) == 0

    def test_arquivo_com_erro_retorna_um(self, tmp_path, icones):
        arquivo = escrever_yaml(tmp_path, YAML_ICONE_AUSENTE)
        assert main([str(arquivo), "--icones", str(icones)]) == 1

    def test_pasta_com_todos_validos_retorna_zero(self, tmp_path, icones):
        escrever_yaml(tmp_path, YAML_VALIDO, "a.yaml")
        escrever_yaml(tmp_path, YAML_VALIDO, "b.yaml")
        assert main([str(tmp_path), "--icones", str(icones)]) == 0

    def test_pasta_com_erro_retorna_um(self, tmp_path, icones):
        escrever_yaml(tmp_path, YAML_VALIDO, "ok.yaml")
        escrever_yaml(tmp_path, YAML_ICONE_AUSENTE, "erro.yaml")
        assert main([str(tmp_path), "--icones", str(icones)]) == 1

    def test_pasta_icones_inexistente_retorna_um(self, tmp_path):
        arquivo = escrever_yaml(tmp_path, YAML_VALIDO)
        assert main([str(arquivo), "--icones", str(tmp_path / "nao-existe")]) == 1

    def test_alvo_invalido_retorna_um(self, tmp_path, icones):
        assert main([str(tmp_path / "fantasma.yaml"), "--icones", str(icones)]) == 1

    def test_pasta_vazia_retorna_zero(self, tmp_path, icones):
        pasta = tmp_path / "vazia"
        pasta.mkdir()
        assert main([str(pasta), "--icones", str(icones)]) == 0
