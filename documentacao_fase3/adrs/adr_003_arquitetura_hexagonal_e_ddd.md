# ADR 003: Arquitetura hexagonal com Domain Driven Design

Data: 13/09/2026

Status: Aceita

## Contexto

A Fase 2 já organizava a aplicação em camadas inspiradas em DDD, mas os casos de uso chamavam diretamente o código de acesso ao SQLite. Na Fase 3 foi preciso trocar o SQLite pelo PostgreSQL, enviar métricas ao Datadog e adicionar a verificação de saúde do banco. Nada disso podia alterar as regras de negócio já validadas pelos testes. A equipe é pequena e o prazo é curto, então a solução não podia depender de frameworks de injeção de dependência nem de reescrever a aplicação.

## Decisão

Adotamos a arquitetura hexagonal, com portas e adapters, sobre o modelo de domínio já existente. O arquivo `domain.py` concentra as entidades, as validações de CPF, CNPJ e placa, o status do cliente e as transições permitidas da ordem de serviço. O arquivo `ports.py` define as interfaces que a aplicação conhece: os repositórios, a verificação de saúde do banco e as métricas.

Os casos de uso, em `application.py`, dependem somente dessas portas. O arquivo `infrastructure.py` implementa os adapters concretos para o PostgreSQL e para o envio de métricas via DogStatsD. O arquivo `web.py` é o adapter HTTP, com as rotas, a autorização por papel e o Swagger. O `app.py` funciona como raiz de composição: cria os adapters concretos e os injeta na camada de aplicação.

## Consequências

### Positivas

* A migração para o PostgreSQL ficou restrita ao `infrastructure.py`.
* As métricas e a saúde do banco entraram como novas portas, sem acoplar os casos de uso ao Datadog.
* O domínio pode ser testado sem banco nem HTTP.

### Negativas

* O projeto ganha mais arquivos e uma camada de indireção.
* A injeção é feita por variáveis de módulo. É simples, mas não tem a verificação que um container de injeção de dependência ofereceria.

## Alternativas consideradas

* Manter as camadas da Fase 2 com acesso direto ao banco: descartado porque a troca de banco e a inclusão das métricas espalhariam mudanças pelos casos de uso.
* Usar um ORM, como SQLAlchemy, com repositórios genéricos: descartado porque a troca exigiria reescrever todas as consultas e o projeto já usa SQL explícito com recursos específicos do PostgreSQL.
* Adotar um framework de injeção de dependência: descartado por acrescentar uma dependência sem ganho proporcional ao tamanho da aplicação.
