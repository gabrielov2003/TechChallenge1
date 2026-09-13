# ADR 004: Quatro repositórios com contratos pelo SSM Parameter Store

Data: 13/09/2026

Status: Aceita

## Contexto

O desafio exige quatro repositórios separados, cada um com CI/CD e deploy automático para a nuvem. Esses repositórios dependem uns dos outros: o banco precisa da rede criada junto com o cluster, a API precisa do banco e dos segredos, e o gateway precisa do endereço da API. Os repositórios são públicos, então nenhum valor sensível pode ser copiado para eles. A escolha da AWS como provedor ([RFC 001](../rfcs/rfc_001_provedor_de_nuvem.md)) torna o SSM Parameter Store disponível para essa troca.

## Decisão

Dividimos o sistema em quatro repositórios, cada um com pipeline própria:

* `fiap_tech_challenge_oficina_infra_k8s` provisiona VPC, EKS, ECR, metrics-server, Datadog e os segredos de cada ambiente.
* `fiap_tech_challenge_oficina_infra_database` provisiona o RDS PostgreSQL.
* `fiap_tech_challenge_oficina_api` implanta a aplicação no EKS.
* `fiap_tech_challenge_oficina_auth_lambda` provisiona a Lambda de autenticação e o API Gateway.

Os repositórios de Terraform guardam o estado em um bucket S3 com versionamento e lock nativo, cada um com a sua chave: `infra-k8s/terraform.tfstate`, `infra-database/terraform.tfstate` e `auth-lambda/<env>.tfstate`.

A troca de informações entre os repositórios acontece exclusivamente por parâmetros do SSM Parameter Store, sob o prefixo `/oficina`:

* O `infra_k8s` publica os dados de rede (`/oficina/network/*`), o nome do cluster (`/oficina/eks/cluster_name`) e os segredos de cada ambiente (`/oficina/<env>/jwt_secret`, `webhook_token` e `admin_password`).
* O `infra_database` publica os dados de conexão do banco (`/oficina/db/*`).
* O pipeline da API publica o endereço do LoadBalancer (`/oficina/<env>/api_url`), que a Lambda usa para configurar o gateway.
* A Lambda publica a URL do gateway (`/oficina/<env>/gateway_url`).

No primeiro deploy, a ordem é `infra_k8s`, `infra_database`, API e `auth_lambda`.

## Consequências

### Positivas

* Baixo acoplamento: cada repositório lê apenas os parâmetros de que precisa.
* Os segredos nunca passam pelo repositório nem pelos secrets do GitHub.
* Cada pipeline evolui e faz deploy de forma independente.

### Negativas

* O primeiro deploy precisa seguir a ordem definida.
* Mudanças no nome ou no formato de um parâmetro precisam ser coordenadas entre os repositórios.
* Os parâmetros do SSM são regionais, então a variável `AWS_REGION` precisa ser igual nos quatro repositórios.

## Alternativas consideradas

* `terraform_remote_state`: descartado porque acopla um repositório ao formato do estado do outro e exige acesso de leitura ao estado inteiro, inclusive aos valores sensíveis.
* Monorepo: descartado porque não atende o requisito de quatro repositórios.
* Copiar os valores manualmente para os secrets do GitHub: descartado porque é sujeito a erro e tira os segredos da nuvem.
