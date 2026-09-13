# ADR 005: Ambientes dev e prod na mesma infraestrutura

Data: 13/09/2026

Status: Aceita

## Contexto

O desafio exige a branch main protegida, Pull Request obrigatório e deploy automático das branches de homologação e produção. Pelo lado econômico, duplicar toda a infraestrutura (dois clusters EKS, dois RDS e dois NAT Gateways) dobraria o custo, que já é o maior risco de um projeto acadêmico em uma conta com créditos limitados. Pelo lado técnico, a homologação precisa ser real, com a mesma infraestrutura da produção, para validar as mudanças antes de promovê-las.

## Decisão

Mantemos uma única VPC, um único cluster EKS e uma única instância RDS, e separamos os ambientes de forma lógica. A branch `dev` implanta o ambiente de homologação `dev`, e a branch `main` implanta o ambiente de produção `prod`.

Cada ambiente tem o seu namespace no EKS, o seu schema no PostgreSQL, os seus segredos no SSM (`/oficina/dev/*` e `/oficina/prod/*`), a sua Lambda (`oficina-auth-dev` e `oficina-auth-prod`), o seu API Gateway (`oficina-gateway-dev` e `oficina-gateway-prod`), o seu LoadBalancer e o seu environment no GitHub. Nos repositórios da API e da Lambda, os pipelines definem a variável `ENV` com o valor `prod` na `main` e `dev` nas demais branches.

Nos repositórios de infraestrutura compartilhada, a branch `dev` e os Pull Requests executam apenas o `terraform plan`, e o `apply` acontece somente no push para a `main`. A `main` é protegida: aceita mudanças apenas por Pull Request e exige os checks obrigatórios, que são `test` na API e na Lambda e `validate` nos repositórios de infraestrutura.

## Consequências

### Positivas

* O custo é de uma infraestrutura só, com homologação real antes da produção.
* Promover uma versão para produção é abrir um Pull Request de `dev` para `main`.

### Negativas

* O isolamento é lógico, não físico: a carga em dev consome recursos do mesmo cluster e do mesmo banco.
* Uma mudança na infraestrutura compartilhada afeta os dois ambientes. O `plan` na branch `dev` funciona como revisão antes do `apply`.

## Alternativas consideradas

* Duas infraestruturas completas, uma por ambiente: descartada porque dobraria o custo.
* Um cluster por ambiente com banco compartilhado: descartada porque o plano de controle do EKS é o item mais caro por hora e o ganho de isolamento não compensa no escopo.
* Apenas o ambiente de produção: descartada porque não atende o requisito de deploy automático da branch de homologação.
