# Monitoramento no Datadog: onde mostrar cada requisito

Guia curto para a gravação. Abra o Datadog no site da sua conta (o mesmo do `DD_SITE`). Se não achar um menu, use a busca do topo (Ctrl+K) e digite o nome da tela.

## Antes de mostrar

1. Gere tráfego com o [guia do Postman](testes_postman.md), passos 11 a 19. O passo 19 (webhook com token errado, 6 vezes) faz o alerta de integrações disparar.
2. Em todas as telas, use o ambiente `prod` e o período Past 1 Hour.

## Onde está cada requisito do PDF

| Requisito | Onde mostrar |
|---|---|
| Latência das APIs | Dashboard, gráfico "Latência média da API por endpoint (segundos)". Detalhe em APM, `oficina-api` |
| CPU e memória do Kubernetes | Dashboard, gráficos "CPU dos pods da API", "Memória dos pods da API" e "Réplicas disponíveis da API (HPA)" |
| Healthchecks e uptime | Dashboard, "Healthcheck da API", e o monitor "[Oficina] API fora do ar (healthcheck)" |
| Alertas de falhas no processamento de OS | Monitor "[Oficina] Falhas no processamento de ordens de serviço" e o gráfico de mesmo nome no dashboard |
| Logs JSON com correlação | Logs, busca por `@correlation_id` |
| Volume diário de OS | Dashboard, "Ordens de serviço abertas nas últimas 24 horas" e "Volume diário de ordens de serviço" |
| Tempo médio por status | Dashboard, "Tempo médio em cada status da OS (segundos)" |
| Erros e falhas nas integrações | Dashboard, "Erros e falhas nas integrações (webhook e Lambda)", e o monitor "[Oficina] Erros nas integrações" |
| Traces em execução | APM, Traces |

## Passo a passo

### 1. Dashboard

1. Dashboards, Dashboard List, abra "Oficina, visão operacional".
2. No topo, deixe a variável `env` em `prod`.
3. Passe pelos gráficos de cima para baixo: OS abertas em 24 horas, volume diário, tempo médio por status, latência por endpoint, requisições e erros, CPU, memória, réplicas do HPA, healthcheck, falhas no processamento de OS e erros nas integrações.

### 2. Monitores (alertas)

1. Monitors, Monitor List (ou Manage Monitors), busque `[Oficina]`. Aparecem os 6 monitores.
2. Abra "[Oficina] Erros nas integrações". Ele deve estar em Alert por causa do webhook errado. Mostre a consulta, o limite e o histórico.
3. Abra "[Oficina] Falhas no processamento de ordens de serviço" e mostre a regra: alerta com mais de 3 falhas em 5 minutos.
4. Mostre que "[Oficina] API fora do ar (healthcheck)" está OK.

### 3. APM: latência e traces

1. APM, Services (ou Software Catalog), abra `oficina-api`. Mostre latência, requisições e erros, e a lista de endpoints logo abaixo.
2. APM, Traces. Filtre `service:oficina-api env:prod` e abra um `POST /api/os`.
3. No flame graph, mostre o span da requisição Flask e os spans das consultas ao PostgreSQL.

### 4. Logs com correlação

1. No Postman, copie o `X-Correlation-ID` da aba Headers de qualquer resposta.
2. Logs, Explorer (ou Logs, Search). Busque `service:oficina-api env:prod @correlation_id:VALOR`.
3. Abra o log e mostre que é JSON: `correlation_id`, método, rota, status, `duration_ms` e `dd.trace_id`.
4. Na aba Trace do mesmo log, mostre o trace ligado a ele.
5. Busque `service:oficina-api erro_integracao` para mostrar os logs do webhook com `integracao` e `motivo`.

### 5. Kubernetes

1. Infrastructure, Kubernetes. Abra a lista de Pods.
2. Filtre `kube_namespace:prod` e `kube_deployment:oficina-api`. Mostre CPU, memória e status dos pods.

### 6. Lambda (opcional)

Se a extensão do Datadog estiver ativa, abra Infrastructure, Serverless e depois `oficina-auth-prod`. Se não estiver, mostre o log group `/aws/lambda/oficina-auth-prod` no CloudWatch.

## Se algo não aparecer

| Sintoma | O que fazer |
|---|---|
| Gráficos vazios | Confira `env` em `prod` e o período. Gere tráfego de novo |
| Monitor de integrações ainda OK | Espere de 1 a 3 minutos depois do webhook errado |
| Tempo por status com valores pequenos | É esperado: a demonstração passa poucos segundos em cada status |
| Nada da Lambda | A extensão só é instalada se o repositório da Lambda tiver o secret `DD_API_KEY` |
