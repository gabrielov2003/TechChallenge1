# ADR 002: Escalabilidade horizontal da API com HPA

Data: 13/09/2026

Status: Aceita

## Contexto

Com mais unidades e clientes, a carga da API varia ao longo do dia, com picos em horário comercial. O desafio exige um cluster Kubernetes com escalabilidade. O cluster tem um node group gerenciado com dois nós `c7i-flex.large`, aceita até três e não tem autoscaler de nós. O orçamento limitado impede manter muitas réplicas fixas o tempo todo. Além disso, a aplicação da Fase 2 guardava o banco em um volume que só um pod podia montar, o que impedia ter mais de uma réplica. Com a migração para o RDS ([RFC 002](../rfcs/rfc_002_banco_de_dados.md)), essa restrição deixou de existir.

## Decisão

Adotamos o HorizontalPodAutoscaler (`autoscaling/v2`) para escalar horizontalmente o Deployment `oficina-api` em cada ambiente, entre 1 e 5 réplicas. O alvo é de 70% de uso de CPU e 80% de uso de memória, calculados sobre os requests do container.

Cada pod solicita 100m de CPU e 512Mi de memória, com limites de 500m e 1Gi, e executa o Gunicorn com 2 workers. O metrics-server, instalado via Helm pelo Terraform do repositório `infra_k8s`, fornece as métricas que o HPA consulta.

Para que as réplicas entrem e saiam com segurança, a API usa uma readiness probe em `/api/ready`, que verifica o acesso ao banco, e uma liveness probe em `/api/health`. A aplicação é stateless: não usa volume persistente e mantém todo o estado no RDS. As tabelas são criadas dentro de um advisory lock, o que permite que várias réplicas iniciem ao mesmo tempo.

## Consequências

### Positivas

* A API escala automaticamente, sem intervenção manual.
* O número de réplicas aparece no dashboard do Datadog.
* O rolling update acontece sem indisponibilidade, graças à readiness probe.

### Negativas

* Os nós não escalam sozinhos. Se as réplicas dos dois ambientes passarem da capacidade dos nós, os pods ficam Pending. A evolução é adotar Cluster Autoscaler ou Karpenter.
* As conexões com o banco crescem com as réplicas, porque cada pod tem 2 workers com pool de até `DB_POOL_MAX` conexões. No máximo dos dois ambientes, isso se aproxima do limite de conexões da `db.t3.micro`. A evolução é usar RDS Proxy ou reduzir o pool.
* CPU e memória não refletem diretamente o volume de ordens de serviço em processamento.

## Alternativas consideradas

* Réplicas fixas: descartadas porque desperdiçam recursos fora de pico e não reagem aos picos.
* Vertical Pod Autoscaler: descartado porque aumenta os recursos de um pod em vez de distribuir a carga, e reinicia os pods para aplicar as mudanças.
* KEDA, com escala por eventos: descartado porque, nesta fase, não existe fila ou evento que represente a carga melhor do que CPU e memória.
