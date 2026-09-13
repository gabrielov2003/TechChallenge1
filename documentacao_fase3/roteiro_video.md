# Roteiro do vídeo de demonstração (até 15 minutos)

O roteiro cobre tudo que o PDF pede para o vídeo: autenticação com CPF, execução da pipeline de CI/CD, deploy automatizado, consumo das APIs protegidas, dashboard de monitoramento com análise ao vivo, e logs e traces em execução. Tudo acontece no ambiente `prod` da AWS, na região `us-east-2`.

## 1. Preparação (antes de gravar)

### 1.1 Informações que você vai usar

| Item | Onde pegar |
|---|---|
| URL do gateway de prod | Console da AWS (região us-east-2), API Gateway, `oficina-gateway-prod`, campo Invoke URL do stage `$default`. Também está no parâmetro `/oficina/prod/gateway_url` e no link do job `deploy` da última execução da `main` no repositório da Lambda (esse link termina em `/auth`) |
| Senha do admin de prod | O valor que você definiu no secret `ADMIN_PASSWORD` do repositório da API. Sem esse secret, Systems Manager, Parameter Store, `/oficina/prod/admin_password`, Show decrypted value. Não mostre isso no vídeo |
| Swagger | `<URL do gateway>/apidocs/`. Confira se abre antes de gravar |

### 1.2 Abas abertas no navegador

1. GitHub, repositório da API: aba Pull requests, aba Actions e a página de regras da branch `main` (Settings, Branches ou Rules).
2. GitHub: aba Actions dos outros três repositórios.
3. Datadog: dashboard "Oficina, visão operacional" com a variável `env` em `prod` e período de 1 hora; APM, serviço `oficina-api`; Logs; Monitors.
4. AWS (us-east-2): EKS `oficina-cluster`, API Gateway, Lambda `oficina-auth-prod`, RDS `oficina-db` e CloudWatch Log groups.
5. O diagrama de componentes no Miro.

### 1.3 Pull Request preparado

No repositório da API, crie uma branch e faça uma mudança pequena. Uma boa é colocar no README a seção "Deploys ativos" com a URL do gateway e do Swagger, que também é pedida na entrega. Abra o Pull Request para `dev` e espere os checks ficarem verdes, mas não faça o merge. O merge acontece durante o vídeo.

### 1.4 Terminal

Use o PowerShell (o terminal do PyCharm serve). Cole isto uma vez, fora da gravação, porque a senha aparece:

```powershell
$gw = 'https://SEU_ID.execute-api.us-east-2.amazonaws.com'
$senha = 'COLE_A_SENHA_DO_ADMIN'

function api($metodo, $rota, $corpo, $token) {
  $h = @{}
  if ($token) { $h.Authorization = "Bearer $token" }
  $p = @{ Method = $metodo; Uri = "$gw/api$rota"; Headers = $h; ContentType = 'application/json; charset=utf-8' }
  if ($corpo) { $p.Body = [Text.Encoding]::UTF8.GetBytes(($corpo | ConvertTo-Json -Depth 5 -Compress)) }
  try { Invoke-RestMethod @p } catch { "HTTP $([int]$_.Exception.Response.StatusCode) " + (($_.ErrorDetails.Message | ConvertFrom-Json).PSObject.Properties.Value -join ' ') }
}

function auth($cpf) {
  $p = @{ Method = 'Post'; Uri = "$gw/auth"; ContentType = 'application/json'; Body = (@{ cpf = $cpf } | ConvertTo-Json -Compress) }
  try { Invoke-RestMethod @p } catch { "HTTP $([int]$_.Exception.Response.StatusCode) " + (($_.ErrorDetails.Message | ConvertFrom-Json).PSObject.Properties.Value -join ' ') }
}

Clear-Host
```

`api` chama a API pelo gateway e mostra os erros como `HTTP 403 mensagem`. `auth` chama a Lambda pelo gateway.

### 1.5 Massa de teste

| Uso | Nome | CPF ou placa |
|---|---|---|
| Ensaio antes de gravar | Ana Costa (ativa) | `98765432100` |
| Ensaio antes de gravar | Bruno Reis (será inativado) | `12345678909` |
| Ensaio antes de gravar | Veículo | `XYZ9876` |
| Gravação | Maria Silva (ativa) | `11144477735` |
| Gravação | João Souza (será inativado) | `39053344705` |
| Gravação | Pedro Lima (opcional, teste de posse) | `22233344405` |
| Gravação | CPF válido não cadastrado | `52998224725` |
| Gravação | CPF inválido | `12345678900` |
| Gravação | Veículo | `ABC1D23` |

### 1.6 Ensaio

De 30 a 60 minutos antes de gravar, rode o roteiro inteiro uma vez com a massa de ensaio. Isso aquece a Lambda, confirma que tudo responde e deixa o dashboard com dados.

## 2. Linha do tempo

| Tempo | Bloco | Requisito do PDF |
|---|---|---|
| 00:00 a 01:00 | 1. Abertura e arquitetura | Contexto |
| 01:00 a 03:00 | 2. Pipeline e início do deploy | Execução da pipeline de CI/CD e deploy automatizado |
| 03:00 a 04:30 | 3. Login do funcionário e cadastros | Consumo das APIs protegidas |
| 04:30 a 06:30 | 4. Autenticação com CPF | Autenticação com CPF |
| 06:30 a 09:00 | 5. Fluxo da OS | Consumo das APIs protegidas |
| 09:00 a 11:30 | 6. Dashboard ao vivo e alerta | Dashboard com análise ao vivo |
| 11:30 a 13:15 | 7. Logs e traces | Logs e traces em execução |
| 13:15 a 14:30 | 8. Resultado do deploy na AWS | Deploy automatizado |
| 14:30 a 15:00 | 9. Encerramento | Resumo |

Se preferir, grave por blocos e junte na edição. Isso evita esperar a pipeline ao vivo.

## 3. Passo a passo

### Bloco 1: abertura e arquitetura (00:00 a 01:00)

1. Mostre o diagrama de componentes.
2. Fale em uma frase o caminho de uma requisição: o usuário chama o API Gateway; `/auth` vai para a Lambda, o resto vai para a API no EKS; os dois usam o RDS; a telemetria vai para o Datadog.
3. Cite os quatro repositórios e que cada um tem a sua pipeline.

### Bloco 2: pipeline e início do deploy (01:00 a 03:00)

1. Mostre a regra da `main`: Pull Request obrigatório e checks obrigatórios.
2. Abra o Pull Request preparado para `dev` e mostre os checks verdes. No job `test`, mostre o PostgreSQL de serviço, os testes com pytest e o Bandit.
3. Faça o merge. Vá em Actions e mostre a execução do push na `dev` com os jobs `test`, `build` e `deploy` (environment `dev`). Deixe rodando.
4. Abra um novo Pull Request de `dev` para `main`. Os checks começam. Deixe rodando e volte nele no bloco 5.
5. Se sobrar tempo, mostre a última execução do `infra_k8s` (validate, plan e apply) para mostrar o Terraform no pipeline.

### Bloco 3: login do funcionário e cadastros (03:00 a 04:30)

```powershell
api GET /health
api GET /ready
api GET /clientes
api POST /login @{username='admin'; senha='errada'}
$admin = (api POST /login @{username='admin'; senha=$senha}).access_token
$maria = api POST /clientes @{nome='Maria Silva'; documento='11144477735'} $admin
$maria
$joao = api POST /clientes @{nome='João Souza'; documento='39053344705'} $admin
$joao
$carro = api POST /veiculos @{placa='ABC1D23'; marca='Fiat'; modelo='Argo'; ano=2022} $admin
$carro
```

Esperado:

1. `status ok` no health e no ready.
2. `HTTP 401 Missing Authorization Header` sem token.
3. `HTTP 401 Credenciais inválidas` com a senha errada.
4. Os ids do cliente e do veículo criados.

Se os dados já existirem (`HTTP 400 Documento já cadastrado` ou `Placa já cadastrada`), busque os registros:

```powershell
$maria = api GET /clientes/documento/11144477735 $null $admin
$joao = api GET /clientes/documento/39053344705 $null $admin
$carro = api GET /veiculos/placa/ABC1D23 $null $admin
```

O que falar: a rota exige token e o login do funcionário gera um JWT de perfil admin. A senha do admin vem de um secret do GitHub Actions (ou do SSM, gerada pelo Terraform) e não fica no código.

### Bloco 4: autenticação com CPF (04:30 a 06:30)

```powershell
auth '12345678900'
auth '52998224725'
api PUT "/clientes/$($joao.id_cliente)" @{nome='João Souza'; documento='39053344705'; status='inativo'} $admin
auth '39053344705'
$r = auth '11144477735'
$r
$cliente = $r.access_token
```

Esperado:

1. `HTTP 400 CPF inválido`.
2. `HTTP 404 Cliente não encontrado`.
3. Mensagem de cliente atualizado.
4. `HTTP 403 Cliente inativo`.
5. `access_token`, `token_type Bearer` e `expires_in 3600`.

Para mostrar o conteúdo do token sem colar em site externo:

```powershell
$carga = $cliente.Split('.')[1].Replace('-', '+').Replace('_', '/'); $carga += '=' * ((4 - $carga.Length % 4) % 4); [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($carga))
```

O que falar: a Lambda valida os dígitos, confere se o cliente existe e está ativo no RDS e assina o token com o segredo do ambiente. O token tem `sub` com o id da Maria, `role` cliente e validade de 1 hora. Se der tempo, mostre a Lambda no console e as rotas no API Gateway.

### Bloco 5: fluxo da OS com APIs protegidas (06:30 a 09:00)

```powershell
api GET /os
api GET /clientes $null $cliente
$os = api POST /os @{id_veiculo=$carro.id_veiculo; servicos=@(@{servico='Troca de óleo'; valor_total=150})} $cliente
$os
$id = $os.id_os
api GET /os $null $cliente
api PUT "/os/$id/status" @{status='Entregue'} $admin
api PUT "/os/$id/status" @{status='Em diagnóstico'} $admin
api POST "/os/$id/pecas" @{peca='Filtro de óleo'; valor_total=80} $admin
api PUT "/os/$id/status" @{status='Aguardando aprovação'} $admin
api GET "/os/$id" | ConvertTo-Json -Depth 5
api POST "/os/$id/aprovacao" @{aprovado=$true} $cliente
api PUT "/os/$id/status" @{status='Em execução'} $admin
api PUT "/os/$id/status" @{status='Finalizada'} $admin
api PUT "/os/$id/status" @{status='Entregue'} $admin
api GET "/os/$id/historico" $null $admin
api GET /os/tempo-medio $null $admin | ConvertTo-Json
1..6 | ForEach-Object { api POST /os/webhook/status @{id_os=$id; status='Em execução'; token='errado'} }
```

Esperado:

1. `HTTP 401` sem token.
2. `HTTP 403 Acesso negado para este perfil` na rota de admin com o token da cliente.
3. OS criada com o dono vindo do token, sem mandar `id_cliente`.
4. A listagem da cliente mostra só as OS dela.
5. `HTTP 400 Transição inválida de 'Recebida' para 'Entregue'`.
6. Orçamento consolidado com total de 230 antes da aprovação.
7. `Orçamento aprovado` com o token da própria cliente.
8. Histórico com todos os status e horários.
9. Tempo médio por status. Os valores são em dias, então aparecem pequenos na demonstração.
10. Seis `HTTP 401 Token inválido` no webhook. Isso gera os logs `erro_integracao` e dispara o alerta de integrações no próximo bloco.

Teste opcional de posse (Pedro não pode aprovar a OS da Maria):

```powershell
$pedro = api POST /clientes @{nome='Pedro Lima'; documento='22233344405'} $admin
$outro = (auth '22233344405').access_token
api POST "/os/$id/aprovacao" @{aprovado=$true} $outro
```

Esperado: `HTTP 403 Acesso negado a esta ordem de serviço`.

No meio deste bloco, volte ao GitHub e faça o merge do Pull Request de `dev` para `main`, se os checks já estiverem verdes. O deploy de produção começa e você volta nele no bloco 8.

### Bloco 6: dashboard ao vivo e alerta (09:00 a 11:30)

Gere tráfego para os gráficos andarem:

```powershell
1..40 | ForEach-Object { api GET "/os/$id/status" | Out-Null; api GET /health | Out-Null }
```

No dashboard "Oficina, visão operacional" (`env` em `prod`), mostre:

1. Ordens de serviço abertas nas últimas 24 horas e volume diário.
2. Tempo médio em cada status da OS.
3. Latência média da API por endpoint.
4. Requisições e erros da API.
5. CPU e memória dos pods da API.
6. Réplicas disponíveis da API (HPA).
7. Healthcheck da API.
8. Falhas no processamento de ordens de serviço.
9. Erros e falhas nas integrações, com as barras do webhook que você acabou de gerar.

Depois vá em Monitors, busque `[Oficina]` e mostre os seis monitores. O "[Oficina] Erros nas integrações" deve estar em alerta por causa dos seis erros do webhook. Pode levar de 1 a 3 minutos para mudar de estado. Abra o monitor e mostre o limite e a mensagem.

O que falar: as métricas de negócio vêm da própria aplicação pelo DogStatsD, e o dashboard e os monitores foram criados pelo Terraform.

### Bloco 7: logs e traces (11:30 a 13:15)

Pegue o id de correlação de uma requisição:

```powershell
$resp = Invoke-WebRequest -UseBasicParsing -Uri "$gw/api/os/$id/status"
$resp.Headers['X-Correlation-ID']
```

1. No Datadog, abra Logs e pesquise `service:oficina-api @correlation_id:COLE_O_ID`. Abra o log e mostre que é JSON: `correlation_id`, método, rota, status, `duration_ms` e `dd.trace_id`.
2. Na mesma tela, abra o trace ligado ao log. Mostre o flame graph com o span da requisição Flask e os spans das consultas ao PostgreSQL.
3. Vá em APM, serviço `oficina-api`, e mostre latência por endpoint, taxa de erros e a lista de traces. Filtre por `POST /api/os` para mostrar a abertura de OS feita no bloco 5.
4. Pesquise `service:oficina-api erro_integracao` para mostrar os logs do webhook com `integracao` e `motivo`.
5. No CloudWatch, abra o log group `/aws/lambda/oficina-auth-prod` e mostre o log `cliente_autenticado` com o `correlation_id`. Se a extensão do Datadog estiver ativa na Lambda, pesquise também `service:oficina-auth` no Datadog.
6. Se sobrar tempo, abra `/aws/apigateway/oficina-gateway-prod` e pesquise o mesmo id de correlação para mostrar o access log do gateway.

### Bloco 8: resultado do deploy na AWS (13:15 a 14:30)

1. No GitHub Actions, mostre as execuções da `dev` e da `main` concluídas, com os jobs verdes e o link do environment no job `deploy`.
2. No EKS, abra Resources, Workloads, namespace `prod`, Deployment `oficina-api`. Mostre os pods e a imagem com a tag do commit que acabou de entrar.
3. Mostre rapidamente a Lambda (imagem do ECR e configuração de VPC), as rotas do API Gateway e o RDS (privado e criptografado).

O console do EKS só mostra os pods se você estiver logado com o mesmo usuário IAM que criou o cluster (o das chaves do GitHub) ou com um ARN listado em `admin_principal_arns`. Como alternativa, abra o CloudShell na região us-east-2 e rode:

```bash
aws eks update-kubeconfig --region us-east-2 --name oficina-cluster
kubectl get pods -n prod
kubectl get hpa -n prod
kubectl get pods -n datadog
```

### Bloco 9: encerramento (14:30 a 15:00)

Resuma o que foi mostrado: autenticação por CPF na Lambda, APIs protegidas pelo gateway, quatro pipelines com deploy automático por ambiente, infraestrutura em Terraform, e monitoramento com dashboard, alertas, logs e traces no Datadog.

## 4. Casos de teste

| ID | Cenário | Chamada | Resultado esperado |
|---|---|---|---|
| TC01 | API no ar | `GET /api/health` | 200, status ok |
| TC02 | Banco acessível | `GET /api/ready` | 200, status ok |
| TC03 | Rota protegida sem token | `GET /api/clientes` | 401, Missing Authorization Header |
| TC04 | Login com senha errada | `POST /api/login` | 401, Credenciais inválidas |
| TC05 | Login do admin | `POST /api/login` | 200 com `access_token` |
| TC06 | CPF com dígito inválido | `POST /auth` com `12345678900` | 400, CPF inválido |
| TC07 | CPF válido não cadastrado | `POST /auth` com `52998224725` | 404, Cliente não encontrado |
| TC08 | Cliente inativo | `POST /auth` com `39053344705` depois de inativar | 403, Cliente inativo |
| TC09 | Cliente ativo | `POST /auth` com `11144477735` | 200 com `access_token`, `token_type` e `expires_in` |
| TC10 | Cliente em rota de admin | `GET /api/clientes` com token de cliente | 403, Acesso negado para este perfil |
| TC11 | Cliente abre OS | `POST /api/os` com token de cliente | 201 com `id_os`; dono vem do token |
| TC12 | Cliente lista as OS | `GET /api/os` com token de cliente | 200, apenas as OS da cliente |
| TC13 | Transição inválida | `PUT /api/os/{id}/status` para Entregue a partir de Recebida | 400, Transição inválida |
| TC14 | Consulta pública da OS | `GET /api/os/{id}` sem token | 200 com o orçamento consolidado |
| TC15 | Cliente aprova o orçamento | `POST /api/os/{id}/aprovacao` com o token da dona | 200, Orçamento aprovado |
| TC16 | Cliente tenta aprovar OS de outro | `POST /api/os/{id}/aprovacao` com o token do Pedro | 403, Acesso negado a esta ordem de serviço |
| TC17 | Histórico e tempo por status | `GET /api/os/{id}/historico` e `GET /api/os/tempo-medio` | 200 com os status, horários e médias |
| TC18 | Webhook com token errado | `POST /api/os/webhook/status` | 401, Token inválido; log `erro_integracao`, métrica e alerta |
| TC19 | Token expirado (opcional, depois de 1 hora) | Qualquer rota protegida | 401, Token has expired |

## 5. Como acessar os logs

| Onde | O que tem | Como chegar | Filtro útil |
|---|---|---|---|
| Datadog Logs | Logs JSON da API, dos pods e do agente | Logs, Explorer | `service:oficina-api env:prod`, `@correlation_id:<id>`, `erro_integracao`, `transicao_rejeitada` |
| Datadog Logs | Logs da Lambda, se a extensão estiver ativa | Logs, Explorer | `service:oficina-auth env:prod` |
| CloudWatch Logs | Logs da Lambda | Log groups, `/aws/lambda/oficina-auth-prod` | Pesquisar pelo `correlation_id` ou por `cliente_autenticado` |
| CloudWatch Logs | Access logs do API Gateway | Log groups, `/aws/apigateway/oficina-gateway-prod` | Pesquisar pelo `requestId` |
| CloudWatch Logs | Plano de controle do EKS | Log groups, `/aws/eks/oficina-cluster/cluster` | Útil só para problemas de acesso ao cluster |
| GitHub Actions | Logs das pipelines | Repositório, Actions, execução, job, etapa | Etapas de teste, build, deploy e Terraform |

## 6. Como acessar o monitoramento do Datadog

| Tela | Caminho no Datadog | O que mostrar |
|---|---|---|
| Dashboard | Dashboards, lista, "Oficina, visão operacional" | Todos os requisitos de dashboard do PDF; troque `env` entre `prod` e `dev` |
| Monitores | Monitors, busca `[Oficina]` | Seis alertas, com estado atual e histórico |
| APM | APM, Services, `oficina-api` | Latência por endpoint, erros, traces e flame graph |
| Logs | Logs, Explorer | Busca por serviço, ambiente e `correlation_id` |
| Kubernetes | Infrastructure, Kubernetes | Pods, deployments e uso de CPU e memória |
| Métricas | Metrics, Explorer | `oficina.os.abertas`, `oficina.os.tempo_status`, `oficina.integracao.erros` |
| Lambda | Serverless (ou Infrastructure, Serverless) | `oficina-auth-prod`, se a extensão estiver ativa |

## 7. Se algo der errado durante a gravação

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `HTTP 401 Token has expired` | O token do admin vale 15 minutos e o da cliente, 1 hora | Rodar de novo o login do admin e o `auth` da cliente |
| `/auth` devolve 404 para um CPF que você cadastrou | O cliente foi criado no outro ambiente (schema dev e prod são separados) | Usar o gateway do mesmo ambiente em que o cliente foi criado |
| `HTTP 503` ou `504` nas rotas `/api` | Pods não prontos ou LoadBalancer ainda subindo | Conferir os pods no EKS e chamar `GET /api/ready` |
| `HTTP 500` no `/auth` | A Lambda não conseguiu falar com o banco | Ver o log group da Lambda no CloudWatch |
| Acentos estranhos nas mensagens da Lambda | Codificação do PowerShell 5 | Não é erro; no PowerShell 7 aparece certo |
| Dashboard sem dados | Período ou ambiente errado no dashboard, ou agente parado | Conferir `env` em `prod`, período de 1 hora e os pods do namespace `datadog` |
| Monitor não entra em alerta | Os monitores avaliam em janelas de alguns minutos | Esperar de 1 a 3 minutos após os erros do webhook |

Não mostre no vídeo a senha do admin, as chaves da AWS ou do Datadog, nem os valores do Parameter Store.
