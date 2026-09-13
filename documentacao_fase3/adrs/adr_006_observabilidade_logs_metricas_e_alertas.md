# ADR 006: Logs estruturados, correlação, métricas de negócio e alertas como código

Data: 13/09/2026

Status: Aceita

## Contexto

O sistema precisa ser monitorado quanto à latência, aos recursos do Kubernetes, à saúde da API, às falhas no processamento de ordens de serviço e aos erros de integração. O desafio também pede logs em JSON correlacionados e dashboards de negócio. Uma requisição atravessa o API Gateway, a API ou a Lambda e o banco, e sem um identificador comum não há como seguir o seu caminho. A ferramenta escolhida foi o Datadog ([RFC 004](../rfcs/rfc_004_ferramenta_de_observabilidade.md)).

## Decisão

Adotamos logs estruturados em JSON no stdout em todos os componentes. Cada log traz timestamp, nível, logger, mensagem e atributos extras, e cada requisição à API gera um log `requisicao` com método, rota, status e duração.

Toda requisição recebe um `correlation_id`: o `X-Correlation-ID` recebido do API Gateway ou, na falta dele, um UUID gerado pela API. Esse identificador aparece em todos os logs da requisição e volta no header da resposta. A Lambda usa o `requestId` do gateway como `correlation_id` e nunca registra o CPF.

A API executa com `ddtrace-run`, que gera os traces e injeta o `dd.trace_id` nos logs. Os pods usam unified service tagging, com as tags `env`, `service` e `version`, e a versão é o commit implantado.

A própria aplicação emite as métricas de negócio pelo DogStatsD: `oficina.os.abertas` para o volume de ordens de serviço, `oficina.os.status_alterado` e `oficina.os.tempo_status` para o fluxo e o tempo em cada status, `oficina.os.falhas` para as falhas no processamento e `oficina.integracao.erros` para os erros no webhook.

O agente do Datadog verifica o `/api/health` por meio de uma anotação no pod. O dashboard "Oficina, visão operacional" e seis monitores são declarados no Terraform, no arquivo `datadog.tf`. Os monitores cobrem falhas no processamento de OS, latência alta, API fora do ar, CPU alta nos pods, erros nas integrações e erros na Lambda.

## Consequências

### Positivas

* Uma requisição pode ser seguida do gateway até o banco pelo `correlation_id` e pelo trace.
* Os requisitos de negócio do dashboard vêm de métricas emitidas pela aplicação, sem consultas pesadas ao banco.
* O dashboard e os alertas podem ser recriados em qualquer conta com um `terraform apply`.

### Negativas

* O projeto depende de um serviço externo.
* A chamada ao `/auth` e a chamada seguinte à API são requisições diferentes, com ids diferentes. A ligação entre elas é feita pelo id do cliente.
* As métricas de CPU e memória por pod só existem no ambiente Kubernetes.

## Alternativas consideradas

* Logs em texto simples: descartados porque não permitem filtrar por atributo nem ligar o log ao trace.
* Métricas de negócio calculadas por consultas periódicas ao banco: descartadas porque sobrecarregariam o RDS e atrasariam o dashboard.
* Dashboards e alertas criados manualmente na interface: descartados porque se perdem ao trocar de conta e não passam por revisão em Pull Request.
