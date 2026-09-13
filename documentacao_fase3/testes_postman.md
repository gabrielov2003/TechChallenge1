# Testes no Postman: autenticação por CPF e APIs protegidas

Guia direto para os testes da gravação, no ambiente `prod` (região us-east-2). Os dados são os mesmos da massa de gravação do [roteiro do vídeo](roteiro_video.md).

## 1. O que pegar antes

| Item | Onde pegar |
|---|---|
| URL do gateway | Console da AWS, API Gateway, `oficina-gateway-prod`, campo Invoke URL. Também em Systems Manager, Parameter Store, `/oficina/prod/gateway_url` |
| Senha do admin | O valor que você definiu no secret `ADMIN_PASSWORD` do repositório da API. Sem esse secret, Parameter Store, `/oficina/prod/admin_password`, Show decrypted value |
| Token do webhook | Parameter Store, `/oficina/prod/webhook_token`, Show decrypted value. Só é usado no webhook válido, que é opcional |

## 2. Configuração do Postman (uma vez)

1. Em Environments, crie o environment `Oficina prod` com estas variáveis:

   | Variável | Valor |
   |---|---|
   | `gw` | URL do gateway, sem barra no final. Exemplo: `https://abc123.execute-api.us-east-2.amazonaws.com` |
   | `admin_senha` | Senha do admin, com o tipo secret para não aparecer no vídeo |
   | `webhook_token` | Token do webhook, também com o tipo secret |
   | `token_admin`, `token_cliente`, `id_cliente`, `id_joao`, `id_veiculo`, `id_os` | Deixe vazio. Os scripts dos passos preenchem |

2. Selecione `Oficina prod` no seletor de environment, no canto superior direito.
3. Requisição com body: aba Body, raw, JSON. O Postman já envia o header `Content-Type: application/json`.
4. Rota protegida: aba Authorization, tipo Bearer Token, campo Token com `{{token_admin}}` ou `{{token_cliente}}`. Isso envia o header `Authorization: Bearer <token>`.
5. Rota pública e `/auth`: aba Authorization, tipo No Auth.
6. Os scripts dos passos vão na aba Scripts, em Post-response (nas versões antigas do Postman, aba Tests). Eles guardam o token ou o id no environment, sem copiar e colar.

## 3. Passo a passo

### Passo 1. API no ar

* `GET {{gw}}/api/health`, No Auth. Esperado: `200` com `{"status": "ok"}`.
* `GET {{gw}}/api/ready`, No Auth. Esperado: `200` com `{"status": "ok"}`, o que confirma o acesso ao banco.

### Passo 2. Rota protegida sem token

* `GET {{gw}}/api/clientes`, No Auth.
* Esperado: `401` com `Missing Authorization Header`.

### Passo 3. Token do admin

* `POST {{gw}}/api/login`, No Auth.
* Body: `{"username": "admin", "senha": "{{admin_senha}}"}`
* Esperado: `200` com `access_token`.
* Script: `pm.environment.set("token_admin", pm.response.json().access_token);`
* Para mostrar o erro, troque a senha por `"errada"`. Esperado: `401` com `Credenciais inválidas`.
* Esse token vale 15 minutos. Se alguma chamada de admin der `401 Token has expired`, repita este passo.

### Passo 4. Cadastrar a Maria

* `POST {{gw}}/api/clientes`, Bearer `{{token_admin}}`.
* Body: `{"nome": "Maria Silva", "documento": "11144477735"}`
* Esperado: `201` com `{"id_cliente": ...}`.
* Script: `pm.environment.set("id_cliente", pm.response.json().id_cliente);`
* Se voltar `400` de documento já cadastrado, use `GET {{gw}}/api/clientes/documento/11144477735` com o mesmo token e o mesmo script.

### Passo 5. Cadastrar o João

* `POST {{gw}}/api/clientes`, Bearer `{{token_admin}}`.
* Body: `{"nome": "João Souza", "documento": "39053344705"}`
* Esperado: `201` com `{"id_cliente": ...}`.
* Script: `pm.environment.set("id_joao", pm.response.json().id_cliente);`
* Se já existir: `GET {{gw}}/api/clientes/documento/39053344705`, com o mesmo script.

### Passo 6. Cadastrar o veículo

* `POST {{gw}}/api/veiculos`, Bearer `{{token_admin}}`.
* Body: `{"placa": "ABC1D23", "marca": "Fiat", "modelo": "Argo", "ano": 2022}`
* Esperado: `201` com `{"id_veiculo": ...}`.
* Script: `pm.environment.set("id_veiculo", pm.response.json().id_veiculo);`
* Se já existir: `GET {{gw}}/api/veiculos/placa/ABC1D23`, com o mesmo script.

### Passo 7. Inativar o João

* `PUT {{gw}}/api/clientes/{{id_joao}}`, Bearer `{{token_admin}}`.
* Body: `{"nome": "João Souza", "documento": "39053344705", "status": "inativo"}`
* Esperado: `200` com `Cliente atualizado`.

### Passo 8. Autenticação por CPF, casos de erro

Todos em `POST {{gw}}/auth`, No Auth:

| Body | Esperado |
|---|---|
| `{"cpf": "12345678900"}` | `400`, CPF inválido |
| `{"cpf": "52998224725"}` | `404`, Cliente não encontrado |
| `{"cpf": "39053344705"}` | `403`, Cliente inativo |

### Passo 9. Token da cliente

* `POST {{gw}}/auth`, No Auth.
* Body: `{"cpf": "11144477735"}`
* Esperado: `200` com `access_token`, `token_type` igual a `Bearer` e `expires_in` igual a `3600`.
* Script: `pm.environment.set("token_cliente", pm.response.json().access_token);`
* Na aba Headers da resposta, mostre o `X-Correlation-ID`.
* Esse token vale 1 hora.

### Passo 10. Cliente em rota de admin

* `GET {{gw}}/api/clientes`, Bearer `{{token_cliente}}`.
* Esperado: `403` com `Acesso negado para este perfil`.

### Passo 11. Cliente abre a OS

* `POST {{gw}}/api/os`, Bearer `{{token_cliente}}`.
* Body: `{"id_veiculo": {{id_veiculo}}, "servicos": [{"servico": "Troca de óleo", "valor_total": 150}]}`
* Esperado: `201` com `{"id_os": ...}`. O dono da OS vem do token, sem mandar `id_cliente`.
* Script: `pm.environment.set("id_os", pm.response.json().id_os);`
* O editor pode marcar `{{id_veiculo}}` em vermelho por estar sem aspas. Pode ignorar, o Postman troca pelo número antes de enviar.

### Passo 12. Cliente lista as próprias OS

* `GET {{gw}}/api/os`, Bearer `{{token_cliente}}`.
* Esperado: `200` só com as OS da Maria.

### Passo 13. Transição inválida

* `PUT {{gw}}/api/os/{{id_os}}/status`, Bearer `{{token_admin}}`.
* Body: `{"status": "Entregue"}`
* Esperado: `400` com `Transição inválida de 'Recebida' para 'Entregue'`.

### Passo 14. Diagnóstico e orçamento

Bearer `{{token_admin}}`, nesta ordem:

| Método e URL | Body | Esperado |
|---|---|---|
| `PUT {{gw}}/api/os/{{id_os}}/status` | `{"status": "Em diagnóstico"}` | `200` |
| `POST {{gw}}/api/os/{{id_os}}/pecas` | `{"peca": "Filtro de óleo", "valor_total": 80}` | `201` |
| `PUT {{gw}}/api/os/{{id_os}}/status` | `{"status": "Aguardando aprovação"}` | `200` |

### Passo 15. Consulta pública do orçamento

* `GET {{gw}}/api/os/{{id_os}}`, No Auth. Esperado: `200` com o serviço, a peça e o total de 230.
* `GET {{gw}}/api/os/{{id_os}}/status`, No Auth. Esperado: `200` com `Aguardando aprovação`.

### Passo 16. Cliente aprova o orçamento

* `POST {{gw}}/api/os/{{id_os}}/aprovacao`, Bearer `{{token_cliente}}`.
* Body: `{"aprovado": true}`
* Esperado: `200` com `Orçamento aprovado`. Com `false`, a OS vai para Recusada e o fluxo termina.

### Passo 17. Execução e entrega

`PUT {{gw}}/api/os/{{id_os}}/status`, Bearer `{{token_admin}}`, um body de cada vez:

1. `{"status": "Em execução"}`
2. `{"status": "Finalizada"}`
3. `{"status": "Entregue"}`

Esperado: `200` em cada um.

Para mostrar o webhook válido, faça o primeiro deles por ele, no lugar do `PUT`:

* `POST {{gw}}/api/os/webhook/status`, No Auth, aba Headers com `X-Webhook-Token` igual a `{{webhook_token}}`.
* Body: `{"id_os": {{id_os}}, "status": "Em execução"}`
* Esperado: `200` com `Status atualizado`.

### Passo 18. Histórico e tempo médio

* `GET {{gw}}/api/os/{{id_os}}/historico`, Bearer `{{token_admin}}`. Esperado: `200` com cada status e o horário de início.
* `GET {{gw}}/api/os/tempo-medio`, Bearer `{{token_admin}}`. Esperado: `200` com as médias em dias.

### Passo 19. Webhook com token errado, para o alerta

* `POST {{gw}}/api/os/webhook/status`, No Auth, aba Headers com `X-Webhook-Token` igual a `errado`.
* Body: `{"id_os": {{id_os}}, "status": "Em execução"}`
* Esperado: `401` com `Token inválido`.
* Clique em Send 6 vezes. Em 1 a 3 minutos o monitor "[Oficina] Erros nas integrações" entra em alerta no Datadog.

### Passo 20 (opcional). Cliente tentando aprovar a OS de outro

1. `POST {{gw}}/api/clientes`, Bearer `{{token_admin}}`, body `{"nome": "Pedro Lima", "documento": "22233344405"}`.
2. `POST {{gw}}/auth`, No Auth, body `{"cpf": "22233344405"}`, script `pm.environment.set("token_pedro", pm.response.json().access_token);`
3. `POST {{gw}}/api/os/{{id_os}}/aprovacao`, Bearer `{{token_pedro}}`, body `{"aprovado": true}`.

Esperado no último: `403` com `Acesso negado a esta ordem de serviço`.

## 4. Ligar a chamada aos logs

Toda resposta traz o header `X-Correlation-ID`. Copie o valor na aba Headers da resposta e pesquise no Datadog, em Logs, `@correlation_id:VALOR`. Para as chamadas ao `/auth`, pesquise o mesmo valor no log group `/aws/lambda/oficina-auth-prod` do CloudWatch.

## 5. Se der erro

| Sintoma | O que fazer |
|---|---|
| `401 Token has expired` | O token do admin vale 15 minutos e o da cliente, 1 hora. Repita o passo 3 ou o passo 9 |
| `401 Missing Authorization Header` numa rota protegida | Confira a aba Authorization: tipo Bearer Token e a variável certa |
| `404` em todas as rotas | Confira se o environment está selecionado e se `gw` está sem barra no final |
| `404 Cliente não encontrado` para um CPF cadastrado | O cliente foi criado em outro ambiente. Use o gateway do mesmo ambiente |
| `415` ou `400` logo no envio | Body em raw e JSON, sem vírgula sobrando |
| `500` no `/auth` | A Lambda não conseguiu falar com o banco. Veja o log group `/aws/lambda/oficina-auth-prod` |
