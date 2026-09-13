# RFC 002: Adoção do PostgreSQL no Amazon RDS

Data: 13/09/2026

Status: Encerrada (aprovada)

## Resumo

Propõe substituir o SQLite em arquivo da Fase 2 por uma instância gerenciada de PostgreSQL 16 no Amazon RDS, compartilhada pelos ambientes com um schema para cada um.

## Problema

Na Fase 2 a aplicação usava SQLite em arquivo, montado em um PersistentVolumeClaim `ReadWriteOnce`, que só pode ser usado por um pod. Na Fase 3 a API passa a rodar com várias réplicas controladas por HPA, a Lambda de autenticação precisa consultar os clientes e o desafio exige banco de dados gerenciado. Além disso, o SQLite não aplicava as chaves estrangeiras declaradas, porque o código não ativava o `PRAGMA foreign_keys`.

A solução precisa atender a estes critérios:

1. Aderência ao modelo relacional do domínio, com integridade referencial aplicada pelo banco.
2. Transações e controle de concorrência para várias réplicas e para a Lambda.
3. Recursos para os relatórios pedidos, como o tempo médio por status.
4. Operação gerenciada: backup, atualização, criptografia e rede privada.
5. Custo compatível com o projeto e elegibilidade ao Free Tier.
6. Paridade com o ambiente local em Docker.

## Proposta técnica

Provisionar pelo repositório `infra_database` uma instância do Amazon RDS for PostgreSQL 16 com:

* Classe `db.t3.micro`, 20 GB de armazenamento `gp3` criptografado e aumento automático de disco até 50 GB.
* Backup automático com retenção de 1 dia e atualização automática de versão menor.
* Sem acesso público, nas subnets privadas da VPC do cluster, com security group liberando a porta 5432 apenas para o CIDR da VPC.
* Senha gerada pelo Terraform e publicada como SecureString no SSM.
* Um schema por ambiente (`dev` e `prod`), selecionado pela aplicação com `search_path`.

Na arquitetura atual, a mudança fica restrita aos adapters de repositório (`infrastructure.py`), graças à arquitetura hexagonal ([ADR 003](../adrs/adr_003_arquitetura_hexagonal_e_ddd.md)). A própria aplicação cria as tabelas na inicialização, dentro de um advisory lock, e a Lambda consulta a tabela `cliente` do schema do seu ambiente. O modelo ER e a justificativa completa estão em [banco_de_dados.md](../banco_de_dados.md).

## Impacto esperado

### Benefícios

* Integridade garantida pelo banco com chaves estrangeiras, UNIQUE e CHECK.
* Abertura da OS com itens e histórico em uma única transação.
* Mudança de status protegida contra alterações simultâneas.
* Tempo médio por status calculado com funções de janela.
* API stateless, sem volume persistente, o que libera o HPA.

### Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Instância única, sem Multi AZ | Variável `multi_az` pronta para ser ativada em produção real |
| Limite de conexões da `db.t3.micro` com o HPA no máximo nos dois ambientes | Pool limitado por processo com `DB_POOL_MAX` |
| Dev e prod na mesma instância | Schemas e segredos separados por ambiente |

### Custos

A classe `db.t3.micro` com 20 GB é elegível ao Free Tier. O aumento automático de disco e os backups acima da cota gratuita consomem créditos.

### Restrições

* A Lambda usa o usuário administrador do banco.
* As tabelas são criadas com `CREATE TABLE IF NOT EXISTS`, sem ferramenta de migração versionada.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
|---|---|
| RDS for MySQL | Atenderia o caso, mas perde recursos usados no projeto, como `pg_advisory_xact_lock`, `TIMESTAMPTZ` e schemas por ambiente com `search_path` |
| Aurora PostgreSQL Serverless v2 | Não tem Free Tier e custa mais que uma `db.t3.micro` quando ativo |
| DynamoDB | Modelo chave e valor, sem joins nem integridade referencial; o tempo médio por status exigiria processamento extra na aplicação |
| PostgreSQL em StatefulSet no EKS | Não é gerenciado: backup, atualização e failover ficariam com a equipe, o que não atende o requisito |

## Pontos em aberto

* Ativar Multi AZ quando houver uso em produção real.
* Separar as instâncias de dev e prod quando houver orçamento.
* Avaliar RDS Proxy se o HPA escalar muito.
* Criar um usuário somente leitura na tabela `cliente` para a Lambda.
* Adotar migrações versionadas, como Alembic ou Flyway.
