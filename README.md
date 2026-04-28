# Sistema de Gestão de Oficina Mecânica (MVP) - Fase 1

Este projeto é o **MVP (Minimum Viable Product)** de um sistema de back-end desenvolvido para uma oficina mecânica de médio porte. O objetivo principal é automatizar o fluxo de atendimento, desde a recepção do veículo até a entrega final, resolvendo problemas de desorganização, falhas no controle de estoque e falta de histórico.

## 🛠️ Tecnologias Utilizadas

*   **Python 3.11+ / Flask:** Framework para criação da API RESTful.
*   **SQLite3:** Banco de dados relacional leve.
*   **Pandas:** Utilizado na camada de infraestrutura para manipulação eficiente de dados e geração de relatórios.
*   **Docker & Docker Compose:** Para containerização e execução simplificada do ambiente.
*   **JWT (JSON Web Token):** Autenticação segura para APIs administrativas.
*   **Flasgger (Swagger):** Documentação interativa da API.

## 🏛️ Arquitetura e Organização (DDD)

O projeto segue os princípios de **Domain-Driven Design (DDD)**, organizado em uma arquitetura de camadas para garantir separação de responsabilidades:

*   **`src/domain.py`**: Contém as entidades de negócio (`Clinete`, `Veiculo`, `OrdemServico`) e validações de dados sensíveis como CPF/CNPJ e placas.
*   **`src/application.py`**: Orquestra os casos de uso, como a abertura de OS e a geração automática de orçamentos.
*   **`src/infrastructure.py`**: Gerencia a persistência no SQLite3 e a configuração técnica do banco de dados.
*   **`src/web.py`**: Define os endpoints da API e a documentação Swagger.
*   **`src/app.py`**: Ponto de entrada que inicializa o servidor Flask e o banco de dados.

## 🗄️ Justificativa do Banco de Dados: SQLite

A escolha pelo **SQLite** para este MVP justifica-se pela sua natureza *serverless* e configuração zero, o que permite uma **execução local simples** conforme exigido pelo desafio. Sendo um banco de dados relacional baseado em arquivos, ele garante a integridade dos dados e o histórico de clientes e veículos sem a necessidade de gerenciar um servidor de banco de dados externo nesta fase inicial.

## 🚀 Como Rodar o Projeto

A maneira mais rápida e recomendada de executar a aplicação é utilizando o **Docker**.

### Pré-requisitos
*   Docker instalado.
*   Docker Compose instalado.

### Passo a Passo
1.  **Clone o repositório** e acesse a pasta raiz do projeto.
2.  **Defina a chave secreta** (opcional): No arquivo `docker-compose.yml`, você encontrará a variável `JWT_SECRET_KEY`. Você pode alterá-la para qualquer valor aleatório para garantir a segurança dos tokens.
3.  **Execute o comando de build e inicialização**:
    ```bash
    docker-compose up --build
    ```
4.  **Acesso à API**: O servidor estará disponível em `http://localhost:5000`.
5. Para fazer requisições, você precisa primeiro fazer um GET na rota http://localhost:5000/api/login que irá retornar um TOKEN, este deve ser passado em todas as requisições no headers da seguinte maneira: Authorization=Bearer token_retornado

*Nota: O banco de dados `database.db` será criado automaticamente na primeira execução através do script de infraestrutura integrado ao `app.py`.*

## 📖 Como usar o Swagger (Documentação)

O sistema conta com documentação interativa via **Swagger**, facilitando o teste das rotas e a compreensão dos modelos de dados.

1.  Com o container rodando, acesse no seu navegador:
    **`http://localhost:5000/apidocs/`**
2.  Lá você encontrará todas as rotas disponíveis, como:
    *   **POST `/clientes`**: Cadastro de novos clientes.
    *   **POST `/os`**: Abertura de uma nova Ordem de Serviço.
    *   **GET `/os/{id}`**: Consulta do status e orçamento gerado automaticamente.

## 🔄 Fluxo Principal da Ordem de Serviço (OS)

O sistema gerencia o ciclo de vida completo da OS conforme definido no **Event Storming**:
1.  **Identificação**: Cliente identificado por documento (CPF/CNPJ).
2.  **Abertura**: OS criada com status inicial **"Recebida"**.
3.  **Diagnóstico**: O mecânico adiciona peças e serviços, e o sistema gera o orçamento automático.
4.  **Acompanhamento**: A OS progride pelos status: *Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada → Entregue*.

Gabriel, aqui vai um trecho direto e pronto pra colar no seu README:

---

## 🧪 Testes Unitários

O projeto possui testes automatizados utilizando a biblioteca padrão do Python, o `unittest`. Esses testes validam o funcionamento das principais rotas da API, incluindo:

* Autenticação (`/login`)
* Cadastro e consulta de clientes
* Cadastro e consulta de veículos
* Criação e atualização de Ordens de Serviço (OS)
* Adição de serviços e peças
* Geração do orçamento consolidado

Os testes foram estruturados de forma independente, garantindo maior confiabilidade e evitando dependência entre execuções.

### ▶️ Como executar os testes

Na raiz do projeto, execute o comando:

```bash
python -m unittest tests/unit_tests.py
```

### ⚠️ Observações

* Certifique-se de que as dependências do projeto estejam instaladas.
* Os testes utilizam um banco SQLite local (`instance/database.db`), que será criado automaticamente caso não exista.
* Para evitar conflitos de dados (como CPF ou placa duplicados), os testes geram valores aleatórios durante a execução.

---
*Este projeto faz parte do Tech Challenge da Pós-Graduação em Arquitetura de Software da FIAP.*