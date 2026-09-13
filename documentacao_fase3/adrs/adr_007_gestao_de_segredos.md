# ADR 007: Segredos gerados pelo Terraform e guardados no SSM

Data: 13/09/2026

Status: Aceita

## Contexto

Os repositórios são públicos. Na Fase 2 os segredos da aplicação (chave do JWT e token do webhook) ficavam como secrets do GitHub, e o kubeconfig era copiado manualmente. Na Fase 3 surgem mais segredos, como a senha do banco e a senha do admin. Alguns deles precisam ser iguais em componentes de repositórios diferentes, como a chave do JWT, que a Lambda usa para assinar e a API para validar ([RFC 003](../rfcs/rfc_003_estrategia_de_autenticacao.md)). Segredos digitados por pessoas tendem a ser fracos e a vazar em mensagens e arquivos locais.

## Decisão

Geramos todos os segredos da aplicação com o recurso `random_password` do Terraform. A senha do banco é gerada no repositório `infra_database`. A chave do JWT, o token do webhook e a senha inicial do admin são gerados no repositório `infra_k8s`, um de cada para cada ambiente. Todos os valores ficam no SSM Parameter Store como SecureString.

O pipeline da API lê esses parâmetros, mascara os valores no log do GitHub Actions e cria o Secret do Kubernetes no namespace do ambiente. A Lambda recebe os valores como variáveis de ambiente durante o `terraform apply`. A senha do admin é a exceção: se o secret `ADMIN_PASSWORD` existir no GitHub, o pipeline usa esse valor no lugar do gerado, e a API atualiza a senha do admin ao subir, o que permite trocá-la sem mexer no Terraform. Fora isso, o GitHub guarda apenas as chaves de acesso da AWS e as chaves do Datadog. O arquivo `.env` nunca é versionado, e o `.env.example` contém apenas valores de exemplo.

## Consequências

### Positivas

* Nenhum valor sensível fica no repositório público nem é digitado por pessoas.
* A rotação é feita regenerando o recurso no Terraform e fazendo um novo deploy.
* O kubeconfig deixa de ser um secret, porque o pipeline gera o acesso ao cluster com as credenciais da AWS.

### Negativas

* Os segredos aparecem nas variáveis de ambiente da Lambda e no estado do Terraform. O bucket de estado é privado e versionado. A evolução é ler os valores do SSM ou do Secrets Manager em tempo de execução.
* A Lambda usa o usuário administrador do banco. A evolução é criar um usuário somente leitura na tabela `cliente`.

## Alternativas consideradas

* Manter os segredos como secrets do GitHub: descartado porque exige cópia manual e não resolve o compartilhamento entre repositórios.
* AWS Secrets Manager: descartado nesta fase porque cobra por segredo armazenado, e a rotação automática que ele oferece ainda não é necessária.
* Sealed Secrets ou External Secrets Operator no cluster: descartados porque acrescentam componentes ao cluster e não atendem a Lambda.
