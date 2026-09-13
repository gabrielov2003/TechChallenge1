# RFC 004: Adoção do Datadog para monitoramento e observabilidade

Data: 13/09/2026

Status: Encerrada (aprovada)

## Resumo

Propõe usar o Datadog como ferramenta única de métricas, traces, logs, verificações de saúde, dashboards e alertas, com agente no EKS, `ddtrace` na API e extensão na Lambda.

## Problema

A direção da oficina quer detectar gargalos em tempo real. O desafio pede integração com Datadog ou New Relic para monitorar a latência das APIs, CPU e memória do Kubernetes, healthchecks e uptime, alertas para falhas no processamento de ordens de serviço e logs estruturados em JSON com correlação entre requisições. Também pede dashboards com volume diário de OS, tempo médio por status e erros nas integrações. Na Fase 2 não havia nenhuma ferramenta de monitoramento, e os logs eram texto simples.

A solução precisa atender a estes critérios:

1. Cobrir todos os sinais pedidos (infraestrutura, APM, logs, verificações de saúde, métricas de negócio e alertas) em uma ferramenta só.
2. Exigir pouco esforço de instrumentação em Python com Flask, no Kubernetes e na Lambda.
3. Permitir dashboards e alertas versionados como código.
4. Ter custo compatível com o projeto.

## Proposta técnica

1. Instalar o agente e o Cluster Agent do Datadog no EKS pelo Terraform do `infra_k8s`, via Helm, com coleta de logs de todos os containers, APM, DogStatsD e métricas de estado do Kubernetes.
2. Executar a API com `ddtrace-run`, que gera os traces e injeta `dd.trace_id` nos logs, e enviar as métricas de negócio pelo DogStatsD.
3. Configurar a verificação HTTP (`http_check`) do `/api/health` por anotação no pod.
4. Incluir a extensão do Datadog na imagem da Lambda quando a API key estiver configurada.
5. Declarar o dashboard "Oficina, visão operacional" e seis monitores no `datadog.tf`.

Cada requisito do desafio fica atendido assim:

| Requisito do desafio | Como é atendido |
|---|---|
| Latência das APIs | APM do serviço `oficina-api` e métrica `trace.flask.request.duration` por endpoint |
| CPU e memória do Kubernetes | Métricas `kubernetes.cpu.usage.total` e `kubernetes.memory.usage` dos pods e réplicas disponíveis do HPA |
| Healthchecks e uptime | `http_check` no `/api/health` e monitor "API fora do ar" |
| Alertas de falhas no processamento de OS | Métrica `oficina.os.falhas` e monitor dedicado |
| Logs JSON com correlação | Logs estruturados com `correlation_id` e `dd.trace_id` |
| Volume diário de OS | Métrica `oficina.os.abertas` somada por dia |
| Tempo médio por status | Distribuição `oficina.os.tempo_status` agrupada por `status` |
| Erros nas integrações | Métrica `oficina.integracao.erros` (webhook) e erros da Lambda |

## Impacto esperado

### Benefícios

* Métricas, traces e logs na mesma ferramenta, ligados pelas tags `env`, `service` e `version`. Isso permite sair de um alerta, abrir o trace da requisição e chegar ao log correspondente.
* Dashboard e alertas recriáveis em qualquer conta com um `terraform apply`.

### Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Fim do período de trial | Gravar a demonstração dentro do trial; dashboard e monitores como código permitem recriar tudo em outra conta |
| Vazamento das chaves do Datadog | As chaves ficam apenas em secrets do GitHub e em `set_sensitive` no Helm, nunca no repositório |
| Volume de logs com a coleta de todos os containers | Filtrar namespaces se o volume crescer |

### Custos

O trial de 14 dias cobre todos os recursos. Depois dele, APM e logs passam a ser pagos.

### Restrições

O projeto passa a depender de um serviço externo. As métricas de CPU e memória por pod só existem no ambiente Kubernetes.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
|---|---|
| New Relic | Tem plano gratuito permanente com cota mensal de ingestão, mas a equipe tem menos familiaridade, e as métricas customizadas e os dashboards como código são menos diretos para o que o projeto precisa |
| CloudWatch com Container Insights | Nativo da AWS, mas com APM, dashboards e correlação de logs menos integrados, custo por métrica customizada e análise ao vivo mais limitada |
| Prometheus e Grafana no cluster | Open source, mas acrescenta componentes para operar em dois nós pequenos; APM e logs exigiriam Tempo e Loki, e alertas e retenção ficariam com a equipe |

## Pontos em aberto

* Definir o que fazer após o trial: plano pago, migração para outra ferramenta ou nova conta.
* Instrumentar a Lambda com a biblioteca do Datadog para gerar traces, além de logs e métricas.
* Definir a retenção de logs e quais namespaces devem ser coletados.
