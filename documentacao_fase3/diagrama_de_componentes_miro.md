# Diagrama de componentes no Miro: passo a passo

O PDF pede um diagrama de componentes com a visão de nuvem, APIs, banco e monitoramento. Este guia lista o que colocar no quadro e em que ordem montar, para você ajustar o visual do seu jeito.

## 1. Inventário do que vai no quadro

| Grupo | Componente | Texto sugerido no card |
|---|---|---|
| Usuários | Cliente | Autentica com CPF e acompanha as próprias OS |
| Usuários | Atendente e Mecânico | Perfil admin, login com usuário e senha |
| Usuários | Sistema externo | Atualiza status pelo webhook |
| GitHub | 4 repositórios | api, auth_lambda, infra_k8s, infra_database |
| GitHub | GitHub Actions | Testes, build, deploy e Terraform |
| GitHub | Environments | dev (branch dev) e prod (branch main) |
| AWS, fora da VPC | API Gateway HTTP API | `oficina-gateway-dev` e `oficina-gateway-prod`; rotas `POST /auth` e `ANY /{proxy+}`; throttling |
| AWS, fora da VPC | Amazon ECR | Imagens da API e da Lambda |
| AWS, fora da VPC | SSM Parameter Store | Contratos e segredos em `/oficina/...` |
| AWS, fora da VPC | CloudWatch Logs | Logs da Lambda, access logs do gateway e plano de controle do EKS |
| AWS, fora da VPC | Amazon S3 | Estado do Terraform |
| VPC, subnets públicas | NAT Gateway | Saída para a internet das subnets privadas |
| VPC, subnets públicas | Load Balancer | Um por ambiente, criado pelo Service da API |
| VPC, subnets privadas | Amazon EKS `oficina-cluster` | Kubernetes 1.34, node group com 2 nós `c7i-flex.large` |
| Dentro do EKS | Namespace `prod` e namespace `dev` | Deployment `oficina-api`, Service, HPA de 1 a 5 réplicas, ConfigMap, Secret |
| Dentro do EKS | Namespace `kube-system` | metrics-server, CoreDNS, VPC CNI |
| Dentro do EKS | Namespace `datadog` | Agent (um por nó) e Cluster Agent |
| VPC, subnets privadas | AWS Lambda | `oficina-auth-dev` e `oficina-auth-prod`, imagem de container |
| VPC, subnets privadas | Amazon RDS | PostgreSQL 16, `db.t3.micro`, schemas `dev` e `prod` |
| Externo | Datadog | Dashboard, 6 monitores, APM, Logs |
| Externo | Email | Notificação dos alertas |

## 2. Layout sugerido

| | Coluna 1 | Coluna 2 | Coluna 3 | Coluna 4 |
|---|---|---|---|---|
| Topo | | GitHub (repositórios, Actions, environments) | | |
| Meio | Usuários | AWS: API Gateway, ECR, SSM, CloudWatch, S3 | | Datadog e Email |
| Base | | VPC: subnets públicas (NAT, Load Balancers) | VPC: subnets privadas (EKS, Lambda, RDS) | |

A ideia é o fluxo das requisições andar da esquerda para a direita (usuário, gateway, API, banco), o CI/CD ficar em cima e o monitoramento na direita.

## 3. Montagem

1. Crie um board novo e dê o título "Oficina, arquitetura de componentes, Fase 3". Se quiser um ponto de partida, a galeria de templates do Miro tem modelos de arquitetura AWS.
2. Ative os ícones da AWS. Na barra lateral, abra a biblioteca de formas, procure por AWS e adicione o pacote de ícones oficiais. Para GitHub e Datadog, use a busca de ícones ou suba o logo como imagem.
3. Desenhe os contêineres, do maior para o menor:
   1. Um retângulo grande com borda laranja para "AWS, região us-east-2".
   2. Dentro dele, um retângulo com borda tracejada para a "VPC 10.0.0.0/16".
   3. Dentro da VPC, duas faixas: "Subnets públicas" e "Subnets privadas", com a anotação "2 zonas de disponibilidade".
   4. Dentro das subnets privadas, um retângulo para o "EKS oficina-cluster" e, dentro dele, um retângulo por namespace (`prod`, `dev`, `kube-system`, `datadog`).
   5. Fora da AWS, um retângulo para "GitHub" no topo e outro para "Datadog" na direita.
4. Coloque os ícones e cards do inventário da seção 1 nos contêineres certos. Em cada card, nome em cima e detalhe embaixo, em fonte menor.
5. Ligue os componentes com os conectores da seção 4, sempre com rótulo. Use três estilos de linha:
   * Contínua azul para requisições dos usuários.
   * Tracejada roxa para observabilidade (métricas, traces e logs).
   * Pontilhada cinza para CI/CD e provisionamento.
6. Numere as setas do fluxo principal (1 a 9) com círculos pequenos. São os mesmos números do diagrama de sequência.
7. Adicione uma legenda no canto com os três estilos de linha e o significado dos números.
8. Revise com o checklist da seção 5.
9. Exporte e compartilhe:
   * Menu do board, Export, PNG em alta qualidade ou PDF. Salve a imagem nesta pasta, por exemplo em `imagens/diagrama_componentes.png`.
   * Botão Share, acesso "qualquer pessoa com o link pode ver", para colocar o link no PDF da entrega.
10. Para o diagrama específico de cada repositório (pedido no README de cada um), duplique o frame e destaque só a parte daquele repositório, deixando o resto em cinza.

## 4. Conectores

| Nº | Origem | Destino | Rótulo | Estilo |
|---|---|---|---|---|
| 1 | Cliente | API Gateway | HTTPS `POST /auth` com CPF | contínua |
| 2 | API Gateway | Lambda | Invocação (AWS_PROXY) | contínua |
| 3 | Lambda | RDS | SQL 5432, consulta cliente e status | contínua |
| 4 | Cliente e Atendente | API Gateway | HTTPS `/api/*` com Bearer JWT | contínua |
| 5 | API Gateway | Load Balancer | HTTP proxy com `X-Correlation-ID` | contínua |
| 6 | Load Balancer | Pods `oficina-api` | HTTP 5000 | contínua |
| 7 | Pods `oficina-api` | RDS | SQL 5432, schema do ambiente | contínua |
| 8 | Sistema externo | API Gateway | `POST /api/os/webhook/status` com token | contínua |
| 9 | Pods `oficina-api` | Datadog Agent (mesmo nó) | DogStatsD UDP 8125 e APM 8126 | tracejada |
| 10 | Datadog Agent | Pods `oficina-api` | `http_check` em `/api/health` | tracejada |
| 11 | Datadog Agent e Cluster Agent | Datadog | Métricas, traces e logs, pela saída do NAT | tracejada |
| 12 | Lambda | Datadog | Logs e métricas pela extensão, se habilitada | tracejada |
| 13 | Lambda e API Gateway | CloudWatch Logs | Logs e access logs | tracejada |
| 14 | Datadog | Email | Alertas dos monitores | tracejada |
| 15 | HPA | metrics-server | CPU e memória dos pods | tracejada |
| 16 | Nós do EKS e Lambda | NAT Gateway | Saída para imagens, Helm e Datadog | contínua fina |
| 17 | GitHub Actions | ECR | Push das imagens com a tag do commit | pontilhada |
| 18 | GitHub Actions | EKS | `kubectl apply` no namespace do ambiente | pontilhada |
| 19 | GitHub Actions | AWS (via Terraform) | `plan` e `apply`, estado no S3 | pontilhada |
| 20 | GitHub Actions | SSM | Lê contratos e segredos, publica a URL da API | pontilhada |

## 5. Checklist antes de exportar

* A visão de nuvem aparece com região, VPC, subnets públicas e privadas.
* As APIs aparecem: gateway com as duas rotas, Lambda e API no EKS.
* O banco aparece com o detalhe de schemas por ambiente.
* O monitoramento aparece com as setas de telemetria até o Datadog.
* Os dois ambientes (dev e prod) estão identificados.
* Todas as setas têm rótulo com protocolo ou ação.
* A legenda explica os estilos de linha.
