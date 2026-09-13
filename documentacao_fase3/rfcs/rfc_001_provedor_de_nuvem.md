# RFC 001: Adoção da AWS como provedor de nuvem

Data: 13/09/2026

Status: Encerrada (aprovada)

## Resumo

Propõe usar a AWS como provedor único da Fase 3, com API Gateway, Lambda, EKS, RDS for PostgreSQL, ECR e SSM Parameter Store, provisionados com Terraform e implantados pelo GitHub Actions.

## Problema

Na Fase 3 a oficina passa a operar em várias unidades, e o sistema precisa de API Gateway, uma function serverless para autenticação, banco de dados gerenciado e cluster Kubernetes com escalabilidade, tudo provisionado com Terraform e com deploy automático. Ao fim da Fase 2 existia apenas um Terraform de VPC e EKS e uma pipeline que publicava em um cluster configurado manualmente. Não havia gateway nem function, e o banco era um arquivo SQLite dentro do cluster.

A solução precisa atender a estes critérios:

1. Cobrir todos os serviços exigidos pelo desafio com serviços gerenciados.
2. Ter provider Terraform maduro e módulos da comunidade.
3. Caber no orçamento de um projeto acadêmico, considerando os créditos de conta nova.
4. Integrar com o Datadog, tanto no Kubernetes quanto na function serverless.
5. Aproveitar o que foi entregue na Fase 2 e a familiaridade da equipe.

## Proposta técnica

Adotar a AWS como provedor único, com os serviços abaixo:

| Necessidade | Serviço |
|---|---|
| API Gateway | Amazon API Gateway, HTTP API, um por ambiente |
| Function serverless | AWS Lambda empacotada como imagem de container |
| Banco gerenciado | Amazon RDS for PostgreSQL 16 |
| Kubernetes | Amazon EKS 1.34 com node group gerenciado |
| Registro de imagens | Amazon ECR |
| Contratos entre repositórios e segredos | AWS Systems Manager Parameter Store |
| Estado do Terraform | Amazon S3 com lock nativo |
| Logs de plataforma | Amazon CloudWatch Logs |

A região é definida pela variável `AWS_REGION` dos repositórios. No deploy atual foi usada `us-east-2`.

A proposta se encaixa na arquitetura existente: o Terraform de VPC e EKS da Fase 2 é reaproveitado no repositório `infra_k8s`, e a aplicação continua sendo o mesmo container, agora publicado no ECR. O HTTP API integra direto com Lambda e com endpoints HTTP, o que resolve o roteamento exigido sem componentes extras, com custo e latência menores que a REST API. O RDS oferece a classe `db.t3.micro`, elegível ao Free Tier, e o Datadog tem agente oficial para EKS via Helm e extensão oficial para Lambda.

## Impacto esperado

### Benefícios

* Todos os requisitos de infraestrutura atendidos com serviços gerenciados de um único provedor.
* Reaproveitamento do Terraform da Fase 2 e uso dos módulos `terraform-aws-modules` para VPC e EKS.
* Maior base de documentação e exemplos do mercado.

### Riscos e mitigação

| Risco | Mitigação |
|---|---|
| EKS, NAT Gateway e LoadBalancers cobram por hora mesmo sem uso | Destruir o ambiente entre as demonstrações, na ordem documentada no README do `infra_k8s` |
| A conta gratuita é encerrada quando os créditos acabam | Acompanhar o saldo no Billing e fazer upgrade para o plano pago se o projeto continuar |

### Custos

O plano de controle do EKS custa US$ 0,10 por hora por cluster, e somam-se a ele o NAT Gateway, os LoadBalancers, os nós e o RDS. Com os dois ambientes ligados, a estimativa fica na faixa de US$ 9 a 10 por dia, coberta pelos créditos de conta nova durante o período de demonstração.

### Restrições

* A conta no plano gratuito só aceita tipos de instância da lista Free Tier. Por isso os nós do EKS usam `c7i-flex.large`.
* A política de organização da conta gratuita bloqueia a criação de provedor OIDC no IAM. Por isso o módulo do EKS usa `enable_irsa = false`, já que nenhum pod usa IAM Roles for Service Accounts.
* A infraestrutura fica acoplada a serviços da AWS. A aplicação continua portável, porque é um container com PostgreSQL padrão que também roda localmente com Docker Compose.

## Alternativas consideradas

| Alternativa | Serviços equivalentes | Motivo do descarte |
|---|---|---|
| Google Cloud | API Gateway ou Apigee, Cloud Run functions, Cloud SQL for PostgreSQL, GKE | O crédito mensal do GKE cobre o plano de controle de um cluster zonal, mas seria preciso reescrever toda a infraestrutura da Fase 2 sem ganho funcional para o escopo |
| Azure | API Management, Azure Functions, Azure Database for PostgreSQL, AKS | O AKS tem camada gratuita sem SLA para o plano de controle, mas também exigiria reescrever a infraestrutura e a equipe tem menos familiaridade com a plataforma |

## Pontos em aberto

* Se o projeto continuar após a entrega, decidir o upgrade para o plano pago antes do fim dos créditos.
* Confirmar a região definitiva. O deploy atual usa `us-east-2`, e o padrão no código é `us-east-1`.
* Avaliar a troca do LoadBalancer público da API por um NLB interno com VPC Link.
