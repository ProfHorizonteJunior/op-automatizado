"""Copia os ícones oficiais AWS das subpastas para a raiz de icones/.

Os ícones foram baixados do pacote oficial AWS Architecture Icons e ficaram
em subpastas como Arch_Storage/64/. Este script os copia para icones/ com
os nomes esperados pelo arquiteturas/plataforma-educacional.yaml.

Uso: python baixar_icones.py
"""
import shutil
import sys
from pathlib import Path

RAIZ_ICONES = Path(__file__).resolve().parent / "icones"

# Mapeamento: nome-esperado-pelo-YAML -> caminho relativo dentro de icones/
MAPA = {
    "Amazon-API-Gateway.svg": (
        "Arch_Networking-Content-Delivery/64/Arch_Amazon-API-Gateway_64.svg"
    ),
    "Amazon-Cognito.svg": (
        "Arch_Security-Identity-Compliance/64/Arch_Amazon-Cognito_64.svg"
    ),
    "AWS-Organizations.svg": (
        "Arch_Management-Governance/64/Arch_AWS-Organizations_64.svg"
    ),
    "Amazon-S3.svg": (
        "Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg"
    ),
    "Amazon-Bedrock.svg": (
        "Arch_Artificial-Intelligence/64/Arch_Amazon-Bedrock_64.svg"
    ),
    "Amazon-SQS.svg": (
        "Arch_App-Integration/64/Arch_Amazon-Simple-Queue-Service_64.svg"
    ),
    "AWS-Cost-Explorer.svg": (
        "Arch_Cloud-Financial-Management/64/Arch_AWS-Cost-Explorer_64.svg"
    ),
    "Amazon-DocumentDB.svg": (
        "Arch_Database/64/Arch_Amazon-DocumentDB_64.svg"
    ),
    "AWS-Management-Console.svg": (
        "Arch_Management-Governance/64/Arch_AWS-Management-Console_64.svg"
    ),
    "Amazon-EventBridge.svg": (
        "Arch_App-Integration/64/Arch_Amazon-EventBridge_64.svg"
    ),
    "Amazon-RDS.svg": (
        "Arch_Database/64/Arch_Amazon-RDS_64.svg"
    ),
    "Amazon-Simple-Storage-Service.svg": (
        "Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg"
    ),
    "Amazon-OpenSearch-Service.svg": (
        "Arch_Analytics/64/Arch_Amazon-OpenSearch-Service_64.svg"
    ),
    # User, Users e Client não existem no pacote AWS — os SVGs
    # genéricos já estão na raiz de icones/ (criados anteriormente).
}


def main() -> int:
    print(f"Copiando ícones oficiais AWS para {RAIZ_ICONES}\n")
    ok = falha = 0

    for nome_destino, caminho_relativo in MAPA.items():
        origem = RAIZ_ICONES / caminho_relativo
        destino = RAIZ_ICONES / nome_destino

        if not origem.exists():
            print(f"  ✗  ORIGEM NÃO ENCONTRADA: {caminho_relativo}")
            falha += 1
            continue

        shutil.copy2(origem, destino)
        print(f"  ✓  {nome_destino}")
        ok += 1

    print(f"\nResumo: {ok} copiados, {falha} falha(s).")
    return 0 if falha == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
