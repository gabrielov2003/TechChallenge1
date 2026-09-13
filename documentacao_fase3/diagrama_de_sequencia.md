# Diagrama de sequência: o que ajustar no diagrama atual

O PDF da Fase 3 pede um diagrama de sequência para o fluxo de autenticação e de abertura de ordens de serviço. O diagrama que existe hoje no repositório ([`diagrama_ddd.png`](../diagrama_ddd.png)) mostra o fluxo de negócio das fases anteriores, em estilo event storming, com os passos 1 a 11 entre Atendente, Cliente, Sistema, Mecânico, Orçamento, Veículo, Ordem de Serviço e Peças.

A sugestão é manter esse diagrama como documentação de domínio e montar o de sequência a partir dele, com os ajustes abaixo.

## 1. Formato

* Participantes em colunas no topo, cada um com a sua linha de vida vertical.
* Mensagens de cima para baixo, na ordem em que acontecem. Linha cheia para chamadas e tracejada para respostas.
* Blocos `alt` para as respostas de erro.
* Dois diagramas, ou duas partes no mesmo quadro: "Autenticação por CPF" e "Abertura da OS".
* Números nas mensagens, iguais aos números das setas do diagrama de componentes, ajudam a ligar os dois.

## 2. Participantes

| Hoje | Como fica |
|---|---|
| Cliente | Continua. Agora ele mesmo chama a API (aplicativo, Postman ou terminal) |
| Atendente | Continua, como "Atendente (perfil admin)" |
| Mecânico | Opcional neste diagrama. As ações dele são as mesmas do atendente (perfil admin) |
| Sistema | Troque por quatro participantes: API Gateway, Lambda de autenticação, API Oficina (EKS) e Banco (RDS PostgreSQL) |
| Orçamento, Veículo, Ordem de Serviço, Peças | Deixam de ser participantes. Viram dados gravados no banco e aparecem nas mensagens |
| (novo) Datadog | Opcional, como último participante recebendo logs e métricas, ou apenas como notas |

## 3. Passos que mudam

| Passo no diagrama atual | Como fica agora |
|---|---|
| 1. Identificar Cliente (CPF/CNPJ) | Vira a autenticação: o cliente envia o CPF para `POST /auth` no API Gateway, que invoca a Lambda. A Lambda valida os dígitos, consulta o cliente e o status no banco e devolve o JWT. Inclua os três `alt` de erro: 400 (CPF inválido), 404 (não cadastrado) e 403 (inativo) |
| 2. Cadastrar/Selecionar Veículo | O atendente faz login (`POST /api/login`) e cadastra cliente (`POST /api/clientes`) e veículo (`POST /api/veiculos`). Vale uma nota: o cliente só consegue se autenticar se já estiver cadastrado e ativo |
| 3. Criar OS, status Recebida | `POST /api/os` pelo gateway com o header `Authorization: Bearer`. A API valida o token e o papel; se for cliente, o id vem do token. Em uma transação grava a OS, os itens e o primeiro registro do histórico de status. Responde 201 com o `id_os` |
| 4 e 5. Diagnóstico e adicionar serviços e peças | Atendente troca o status para "Em diagnóstico" (`PUT /api/os/{id}/status`) e inclui itens (`POST /api/os/{id}/pecas` e `/servicos`). A nota "Consultar estoque em tempo real" deve sair ou virar evolução, porque o estoque não é baixado automaticamente |
| 6 e 7. Gerar e enviar orçamento | Atendente troca o status para "Aguardando aprovação". O cliente consulta o orçamento consolidado em `GET /api/os/{id}` |
| 8. Aprovar/Reprovar reparos | O cliente chama `POST /api/os/{id}/aprovacao` com o próprio token. A API confere se a OS é dele (403 se não for) e muda para "Aprovado" ou "Recusada". Existe também "Solicitado alterações", que volta para "Em diagnóstico" |
| 9. Executar manutenção | Pode passar antes por "Aguardando peças" |
| 10 e 11. Finalizar e entregar | "Finalizada" e "Entregue", pelo atendente ou por um sistema externo via webhook (`POST /api/os/webhook/status`). A data de fechamento é gravada em "Entregue" |

O foco pedido no PDF vai até a abertura da OS. Os passos 4 a 11 podem ficar resumidos ou em um segundo diagrama, com o fluxo de status completo.

## 4. Sequência de referência

Use como roteiro para desenhar. Cada linha é uma mensagem, na ordem.

### Autenticação por CPF

1. Cliente envia `POST /auth` com `{"cpf": "..."}` ao API Gateway.
2. API Gateway invoca a Lambda de autenticação, passando o `requestId`.
3. Lambda valida os dígitos do CPF. `alt` inválido: responde 400 "CPF inválido".
4. Lambda consulta `id_cliente` e `status` na tabela `cliente` do schema do ambiente, no RDS.
5. `alt` cliente não encontrado: responde 404. `alt` status inativo: responde 403.
6. Lambda gera o JWT com `sub` (id do cliente), `role` cliente, `cpf` e validade de 1 hora, assinado com o segredo do ambiente.
7. Lambda responde 200 com `access_token`, `token_type` e `expires_in`, e o header `X-Correlation-ID`. O gateway repassa ao cliente.
8. Nota: log JSON `cliente_autenticado` com o `correlation_id`, sem o CPF.

### Abertura da OS pelo cliente

1. Cliente envia `POST /api/os` ao API Gateway, com `Authorization: Bearer <token>` e o corpo `{"id_veiculo": ..., "servicos": [...]}`.
2. API Gateway sobrescreve o `X-Correlation-ID` com o `requestId` e repassa ao LoadBalancer da API Oficina.
3. API valida assinatura e validade do token. `alt` sem token ou token inválido: 401. `alt` papel sem permissão: 403.
4. API usa o `id_cliente` do token.
5. API abre uma transação no banco: grava a OS com status "Recebida", grava os itens, grava o primeiro registro em `historico_status_os` e confirma. `alt` cliente ou veículo inexistente: 400.
6. API envia a métrica `oficina.os.abertas` ao agente do Datadog e registra o log `os_aberta` com o `correlation_id`.
7. API responde 201 com `{"id_os": ...}` e o gateway repassa ao cliente.

### Abertura da OS pelo atendente

Igual ao fluxo do cliente, com duas diferenças: antes ele faz `POST /api/login` (usuário e senha) e recebe um token de perfil admin, e no corpo da OS ele informa o `id_cliente`.
