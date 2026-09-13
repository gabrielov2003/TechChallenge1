# ADR 001: Comunicação síncrona REST pelo API Gateway

Data: 13/09/2026

Status: Aceita

## Contexto

Clientes, funcionários da oficina e sistemas externos acessam o sistema. O desafio exige um API Gateway para controle e roteamento, e os pontos de entrada são dois: a Lambda de autenticação e a API principal no EKS. É preciso limitar o tráfego, registrar os acessos e correlacionar uma requisição do começo ao fim. Os consumidores são navegadores, ferramentas como Postman e sistemas de terceiros, que falam HTTP e JSON. A abertura de OS precisa devolver o número da ordem na hora. Pelo lado econômico, o projeto precisa de uma solução de baixo custo por requisição. A estratégia de autenticação que depende desse roteamento foi definida na [RFC 003](../rfcs/rfc_003_estrategia_de_autenticacao.md).

## Decisão

Adotamos a comunicação síncrona em HTTPS e JSON para todo acesso externo ao sistema. A única porta de entrada é um HTTP API do Amazon API Gateway por ambiente, chamados `oficina-gateway-dev` e `oficina-gateway-prod`.

O gateway encaminha a rota `POST /auth` para a Lambda de autenticação, por integração `AWS_PROXY` no formato de payload 2.0. Todas as demais rotas passam pela rota `ANY /{proxy+}` e seguem, por integração `HTTP_PROXY`, para o LoadBalancer do Service da API no EKS.

Para correlacionar as requisições, o gateway sobrescreve o header `X-Correlation-ID` com o seu `requestId`. A API registra esse valor em todos os logs da requisição e o devolve na resposta, e a Lambda usa o mesmo `requestId` recebido no evento. O stage do gateway aplica throttling de 50 requisições por segundo, com rajada de 100, e grava access logs em JSON no CloudWatch.

Os sistemas externos atualizam o status das ordens de serviço pelo webhook REST `POST /api/os/webhook/status`, autenticado por token. Os repositórios não se chamam em tempo de execução. Os contratos de infraestrutura trafegam pelo SSM Parameter Store, conforme a [ADR 004](adr_004_repositorios_e_contratos_via_ssm.md).

## Consequências

### Positivas

* Um único ponto de entrada por ambiente, com throttling e access logs.
* Baixa latência e contrato simples, documentado no Swagger (`/apidocs/`).
* Rastreabilidade de ponta a ponta pelo `X-Correlation-ID`.

### Negativas

* Acoplamento temporal: se a API estiver fora do ar, a abertura de OS falha na hora, sem fila.
* O LoadBalancer da API é público e poderia ser chamado sem passar pelo gateway. Uma evolução é usar um NLB interno com VPC Link.
* Não há retentativa automática entre o gateway e a API.

## Alternativas consideradas

* REST API (v1) do API Gateway: oferece mais recursos, mas tem custo e latência maiores, sem necessidade para o escopo.
* Mensageria assíncrona (SQS ou SNS) para abrir OS: descartada porque o cliente precisa da resposta imediata com o número da OS. Fica reservada para notificações futuras.
* gRPC: descartado porque os consumidores são navegadores, Postman e sistemas externos que falam HTTP e JSON.
