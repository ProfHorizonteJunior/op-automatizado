# Pesquisa de Disponibilidade AWS — us-east-1

> Verificação realizada pelo **Pesquisador** em 24/09/2026.  
> Região de referência: **us-east-1 (US East — N. Virginia)**

---

## Resultado por serviço

| Serviço | Disponível em us-east-1? | Observação |
|---|---|---|
| **Amazon Cognito** | ✅ Sim | GA em us-east-1 há anos; endpoint documentado em [docs.aws.amazon.com/general/latest/gr/cognito.html](https://docs.aws.amazon.com/general/latest/gr/cognito.html) |
| **Amazon API Gateway** | ✅ Sim | Disponível em todas as regiões principais; integração com Cognito documentada em [docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-enable-cognito-user-pool.html) |
| **Amazon Bedrock** | ✅ Sim | `bedrock-runtime` e `bedrock-mantle` disponíveis em us-east-1; confirmado em [endpoints-region-availability](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints-region-availability.html) |
| **Amazon Bedrock Guardrails** | ✅ Sim | Claude 3 Haiku e Sonnet com Guardrails em us-east-1; Claude 3 Haiku listado explicitamente como suportado em us-east-1 na [documentação de modelos compatíveis](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported.html) |
| **Amazon OpenSearch Serverless** | ✅ Sim | Endpoint `.aoss.us-east-1.amazonaws.com` confirmado; exemplos de SDK da AWS usam us-east-1 como região padrão nos guias de [serverless-sdk](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-sdk.html) |
| **Amazon RDS for PostgreSQL** | ✅ Sim | Disponível em todas as regiões AWS; Multi-AZ com réplicas suportado em us-east-1 |
| **Amazon S3** | ✅ Sim | Disponível globalmente; us-east-1 é a região padrão original |
| **Amazon EventBridge Scheduler** | ✅ Sim | Confirmado ✓ para US East (N. Virginia) na [tabela de disponibilidade de features](https://docs.aws.amazon.com/eventbridge/latest/userguide/feature-availability.html) |
| **AWS Lambda** | ✅ Sim | Disponível em todas as regiões AWS |

---

## Modelos Anthropic Claude disponíveis em us-east-1 (Bedrock)

| Modelo | ID | Guardrails |
|---|---|---|
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | ✅ Suportado |
| Claude 3 Sonnet | Disponível via inference profile | ✅ Suportado |
| Claude 3.7 Sonnet | Disponível em us-east-1 desde fev/2025 | ✅ Suportado |

> **Recomendação**: usar `claude-3-haiku` para respostas rápidas de chat e
> `claude-3-sonnet` (ou 3.7) para análise de PDI e geração de orientação pedagógica.

---

## Configuração MCP recomendada

O arquivo `.kiro/settings/mcp.json` deve conter os dois servidores abaixo.
O `aws-knowledge-mcp-server` já estava configurado; o `aws-documentation`
foi adicionado para permitir consultas à documentação AWS diretamente no agente.

```json
{
  "mcpServers": {
    "aws-knowledge-mcp-server": {
      "url": "https://knowledge-mcp.global.api.aws",
      "type": "http",
      "disabled": false
    },
    "aws-documentation": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false
    }
  }
}
```

> **Nota**: O arquivo `.kiro/settings/mcp.json` é protegido por permissão de escopo
> do Kiro. Para aplicar a configuração, edite o arquivo manualmente ou via
> **Command Palette → "Open MCP Configuration"**.

---

## Conclusão

Todos os serviços da arquitetura `plataforma-educacional.yaml` estão disponíveis
em **us-east-1**. Nenhum serviço exige substituição ou workaround regional.
A stack pode ser provisionada integralmente nessa região com AWS CDK.
