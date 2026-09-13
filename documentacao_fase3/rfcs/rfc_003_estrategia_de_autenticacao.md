# RFC 003: Autenticação de clientes por CPF com Lambda e JWT

Data: 13/09/2026

Status: Encerrada (aprovada)

## Resumo

Propõe que uma Lambda receba o CPF pelo API Gateway, valide o documento e o status do cliente no banco e emita um JWT que a API valida. Os funcionários continuam com login por usuário e senha na própria API.

## Problema

O desafio exige proteger as rotas sensíveis com autenticação via CPF e uma function serverless que valide o CPF, consulte a existência e o status do cliente na base e devolva um JWT válido para as APIs protegidas. Na Fase 2 só os funcionários se autenticavam, com usuário e senha, e não havia perfil de cliente nem controle de acesso aos dados de cada cliente.

A solução precisa atender a estes requisitos:

1. O cliente se autentica apenas com o CPF.
2. Os dígitos do CPF e o status do cliente (`ativo` ou `inativo`) são validados.
3. O token é aceito pelas rotas protegidas da API.
4. Os funcionários continuam com login próprio.
5. O cliente só acessa os próprios dados.
6. Nenhum segredo fica versionado.

## Proposta técnica

1. A rota `POST /auth` do API Gateway invoca a Lambda `oficina-auth-<env>`.
2. A Lambda normaliza e valida os dígitos verificadores do CPF e responde 400 se forem inválidos.
3. A Lambda consulta `id_cliente` e `status` na tabela `cliente` do schema do ambiente e responde 404 se o cliente não existe ou 403 se está inativo.
4. A Lambda gera um JWT HS256 com `sub` (id do cliente), `role` igual a `cliente`, `cpf`, `iat`, `nbf`, `exp` (validade de 1 hora), `jti`, `type` e `fresh`, no formato esperado pelo Flask-JWT-Extended.
5. O segredo de assinatura é gerado pelo Terraform para cada ambiente e fica no SSM (`/oficina/<env>/jwt_secret`). A Lambda usa o segredo para assinar e a API para validar.
6. Os funcionários autenticam em `POST /api/login` com usuário e senha (hash no banco) e recebem um JWT com `role` igual a `admin`. A senha inicial do admin também é gerada pelo Terraform (`/oficina/<env>/admin_password`).
7. A API aplica autorização por papel com o decorator `papel_requerido`. O cliente só abre OS para si, com o id vindo do token, lista as próprias OS e aprova ou recusa o orçamento das próprias OS. Rotas administrativas devolvem 403 para o cliente.
8. O webhook de status usa um token próprio no header `X-Webhook-Token`, comparado em tempo constante.
9. O CPF nunca é registrado nos logs.

Na arquitetura atual, a Lambda fica em um repositório próprio junto com o API Gateway, e a API mantém a validação dos tokens que já fazia na Fase 2, acrescentando o papel de cliente.

## Impacto esperado

### Benefícios

* A autenticação do cliente fica isolada em um componente serverless, que escala sozinho e não depende do cluster.
* A API continua sendo a única responsável pela autorização, com as mesmas regras para tokens de cliente e de funcionário.
* O formato do token vira um contrato entre a Lambda e a API, coberto por testes nos dois repositórios.

### Riscos e mitigação

| Risco | Mitigação |
|---|---|
| O CPF não é um segredo; quem souber o CPF de um cliente consegue um token | Requisito do desafio; ver pontos em aberto |
| O token não pode ser revogado antes de expirar; inativar o cliente só impede novos tokens | Validade curta de 1 hora |
| Segredo simétrico compartilhado entre Lambda e API | Segredo por ambiente, gerado e guardado no SSM como SecureString, com rotação pelo Terraform e redeploy |

### Custos

A Lambda só é invocada no login, o que mantém o uso dentro da cota gratuita.

### Restrições

As rotas protegidas são validadas na API, e não no gateway. O gateway aplica apenas o throttling.

## Alternativas consideradas

| Alternativa | Como funcionaria | Motivo do descarte |
|---|---|---|
| Amazon Cognito com desafio customizado | User pool com autenticação customizada baseada no CPF | Exige três gatilhos Lambda de desafio e sincronizar os clientes com o user pool; complexidade alta para o escopo |
| Lambda Authorizer no API Gateway | Uma Lambda valida o CPF ou o token a cada requisição | Uma invocação extra, e possivelmente uma consulta ao banco, por requisição, com mais latência e cold start |
| JWT Authorizer nativo do HTTP API | O gateway valida o token antes de repassar | Exige um emissor OIDC com JWKS e chave assimétrica, e os tokens de funcionário são emitidos pela própria API |

## Pontos em aberto

* Adicionar um segundo fator ao login por CPF, como código por email ou SMS.
* Criar uma lista de revogação de tokens por `jti`.
* Mover a validação para o gateway com JWT Authorizer quando houver um emissor OIDC.
* Definir a periodicidade de rotação do segredo de assinatura.
