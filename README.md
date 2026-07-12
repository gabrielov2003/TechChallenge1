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

*   **`src/domain.py`**: Contém as entidades de negócio (`Cliente`, `Veiculo`, `OrdemServico`) e validações de dados sensíveis como CPF/CNPJ e placas.
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
5. Para fazer requisições, você precisa primeiro fazer um **POST** na rota `http://localhost:5000/api/login` com body `{"username": "admin", "senha": "admin123"}`, que irá retornar um TOKEN. Este deve ser passado em todas as requisições no header: `Authorization: Bearer <token>`

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


## 📊 Análise Estática de Código

### Bandit (Segurança)

O relatório completo está em `bandit-report.txt`. A análise identificou **4 ocorrências**:

| Severidade | Descrição |
|---|---|
| 🔴 High | `debug=True` em `app.py` — expõe o debugger do Werkzeug em produção |
| 🟡 Medium | Binding em `0.0.0.0` — expõe o servidor em todas as interfaces |
| 🟡 Medium | Possível SQL injection via f-string em `application.py` (falso positivo — a concatenação é estática) |
| 🟢 Low | `try/except/pass` em `infrastructure.py` na migração de colunas existentes |

O ponto de atenção real é o `debug=True`, que deve ser desabilitado em ambiente de produção. Os demais são aceitáveis para um MVP.

### Pylint (Qualidade)

O relatório completo está em `pylint-report.txt`. A nota obtida foi **6.91/10**. Os avisos são majoritariamente:

- **Ausência de docstrings** em módulos, classes e métodos (C0114, C0115, C0116) — padrão intencional do projeto MVP.
- **Linhas longas** acima de 100 caracteres em alguns arquivos (C0301).
- **Ordem de imports** (C0411) e uma variável redefinida no escopo externo (W0621).

## 🐳 Docker

O `Dockerfile` usa **multi-stage build** e executa a aplicação com usuário não-root (`appuser`). Para desenvolvimento local:

```bash
cp .env.example .env  # ajuste as variáveis se necessário
docker-compose up --build
```

## ☸️ Kubernetes

Os manifestos ficam em `k8s/`. Para aplicar em um cluster já configurado:

```bash
kubectl apply -f k8s/
```

| Arquivo | Recurso | Descrição |
|---|---|---|
| `configmap.yaml` | ConfigMap | Variáveis não-sensíveis (`FLASK_DEBUG`, `DATABASE_PATH`) |
| `secret.yaml` | Secret | Variáveis sensíveis (`JWT_SECRET_KEY`, `WEBHOOK_TOKEN`) |
| `pvc.yaml` | PersistentVolumeClaim | Volume de 1Gi para persistência do banco SQLite |
| `deployment.yaml` | Deployment | Pod da API com limites de CPU/memória e mount do PVC |
| `service.yaml` | Service (LoadBalancer) | Expõe a API na porta 80 |
| `hpa.yaml` | HorizontalPodAutoscaler | Escala de 1 a 5 pods (CPU ≥ 70% ou memória ≥ 80%) |

> **Nota:** A imagem no `deployment.yaml` usa o placeholder `ghcr.io/OWNER/oficina-api:latest` — substituído automaticamente pelo pipeline CI/CD.

## 🏗️ Terraform

Os scripts ficam em `terraform/` e provisionam um cluster **EKS na AWS** com VPC dedicada.

**Recursos criados:**
- VPC com subnets públicas e privadas em 2 AZs
- NAT Gateway para acesso à internet dos nós privados
- Cluster EKS 1.30
- Node Group gerenciado com instâncias `t3.small` (1–3 nós)

**Como aplicar:**

```bash
cd terraform
terraform init
terraform plan
terraform apply
aws eks update-kubeconfig --region us-east-1 --name oficina-cluster
kubectl apply -f ../k8s/
```

**Pré-requisitos:** AWS CLI configurado com credenciais válidas (`aws configure`).

## 🔄 CI/CD (GitHub Actions)

O pipeline em `.github/workflows/ci-cd.yml` executa em todo push para `main`:

| Job | Gatilho | O que faz |
|---|---|---|
| `test` | PR e push | Instala dependências e roda `pytest` |
| `build` | Push para `main` | Build e push da imagem para GHCR (`ghcr.io`) |
| `deploy` | Após `build` | `kubectl apply -f k8s/` + atualiza a imagem do Deployment |

**Secrets necessários no GitHub:**

| Secret | Descrição |
|---|---|
| `KUBECONFIG_B64` | Conteúdo do kubeconfig em base64 (`base64 ~/.kube/config`) |

> `GITHUB_TOKEN` é fornecido automaticamente pelo GitHub para push no GHCR.

## 🖼️ Modelagem Estratégica e Design Orientado a Domínio (DDD)

Como parte integrante da documentação de arquitetura, foi adicionado o arquivo **`diagrama_ddd.png`**. Este documento visual apresenta a modelagem completa do sistema, dividida em duas frentes principais:

*   **Event Storming:** Um mapeamento detalhado dos fluxos de **Criação e Acompanhamento de OS** e **Gestão de Peças**, identificando todos os eventos de domínio, atores (como Atendente, Mecânico e Cliente) e as interações com o sistema.
*   **Diagrama de Domínio:** A representação das entidades core, como `Clinete`, `Veiculo` e `Ordem_Servico`, evidenciando como as regras de negócio e validações de dados sensíveis estão estruturadas conforme os padrões de DDD.

O diagrama ilustra o ciclo de vida completo do atendimento, desde a **identificação do cliente** por CPF/CNPJ até a **entrega final do veículo**, garantindo que o fluxo de status (Recebida, Em diagnóstico, etc.) e a geração automática de orçamentos sigam rigorosamente os requisitos técnicos estabelecidos, e complementa o código-fonte e serve como base para a compreensão da **Linguagem Ubíqua** aplicada em todas as camadas da aplicação.

---
*Este projeto faz parte do Tech Challenge da Pós-Graduação em Arquitetura de Software da FIAP.*