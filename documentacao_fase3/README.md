# Documentação da arquitetura, Fase 3

Esta pasta reúne a documentação arquitetural da Fase 3 do Tech Challenge. O sistema da oficina agora está dividido em quatro repositórios:

| Repositório | Responsabilidade |
|---|---|
| `fiap_tech_challenge_oficina_api` | Aplicação principal, executando no Kubernetes (EKS) |
| `fiap_tech_challenge_oficina_auth_lambda` | Function de autenticação por CPF e API Gateway |
| `fiap_tech_challenge_oficina_infra_k8s` | Rede, cluster EKS, registro de imagens, segredos e monitoramento |
| `fiap_tech_challenge_oficina_infra_database` | Banco de dados gerenciado (RDS PostgreSQL) |

## Conteúdo

Os RFCs e ADRs seguem os modelos da Aula 4 (Propostas Arquiteturais com RFCs e ADRs) da Fase 1. Cada RFC tem Título, Data, Status, Resumo, Problema, Proposta técnica, Impacto esperado, Alternativas consideradas e Pontos em aberto. Cada ADR tem Título, Data, Status, Contexto, Decisão, Consequências e Alternativas consideradas.

### RFCs (decisões técnicas)

| RFC | Título | Status |
|---|---|---|
| [RFC 001](rfcs/rfc_001_provedor_de_nuvem.md) | Adoção da AWS como provedor de nuvem | Encerrada (aprovada) |
| [RFC 002](rfcs/rfc_002_banco_de_dados.md) | Adoção do PostgreSQL no Amazon RDS | Encerrada (aprovada) |
| [RFC 003](rfcs/rfc_003_estrategia_de_autenticacao.md) | Autenticação de clientes por CPF com Lambda e JWT | Encerrada (aprovada) |
| [RFC 004](rfcs/rfc_004_ferramenta_de_observabilidade.md) | Adoção do Datadog para monitoramento e observabilidade | Encerrada (aprovada) |

### ADRs (decisões arquiteturais)

| ADR | Tema |
|---|---|
| [ADR 001](adrs/adr_001_comunicacao_rest_via_api_gateway.md) | Comunicação síncrona REST pelo API Gateway |
| [ADR 002](adrs/adr_002_escalabilidade_com_hpa.md) | Escalabilidade horizontal da API com HPA |
| [ADR 003](adrs/adr_003_arquitetura_hexagonal_e_ddd.md) | Arquitetura hexagonal com DDD |
| [ADR 004](adrs/adr_004_repositorios_e_contratos_via_ssm.md) | Quatro repositórios com contratos pelo SSM |
| [ADR 005](adrs/adr_005_ambientes_dev_e_prod.md) | Ambientes dev e prod na mesma infraestrutura |
| [ADR 006](adrs/adr_006_observabilidade_logs_metricas_e_alertas.md) | Logs estruturados, correlação, métricas e alertas |
| [ADR 007](adrs/adr_007_gestao_de_segredos.md) | Segredos gerados pelo Terraform e guardados no SSM |
| [ADR 008](adrs/adr_008_maquina_de_estados_da_os.md) | Máquina de estados da OS com transição atômica e histórico |

### Demais documentos

| Documento | Conteúdo |
|---|---|
| [banco_de_dados.md](banco_de_dados.md) | Justificativa do banco, diagramas ER antes e depois, ajustes e relacionamentos |
| [diagrama_de_sequencia.md](diagrama_de_sequencia.md) | O que ajustar no diagrama atual para o fluxo de autenticação e abertura de OS |
| [diagrama_de_componentes_miro.md](diagrama_de_componentes_miro.md) | Passo a passo para montar o diagrama de componentes no Miro |
| [roteiro_video.md](roteiro_video.md) | Roteiro do vídeo de 15 minutos, casos de teste, acesso aos logs e ao Datadog |
| [testes_postman.md](testes_postman.md) | Passo a passo dos testes no Postman: token do admin, autenticação por CPF e rotas protegidas |

Os diagramas de componentes e de sequência já estão montados no board do Miro [Oficina Fase 3, diagramas](https://miro.com/app/board/uXjVHn_suZ4=/), prontos para ajustar e exportar.

## Checklist da entrega

* PDF único no Portal do Aluno com os links dos 4 repositórios, do vídeo e das documentações.
* Vídeo de até 15 minutos no YouTube ou Vimeo, público ou não listado.
* Usuário `soat-architecture` adicionado aos 4 repositórios.
* README de cada repositório com o diagrama da arquitetura daquele repositório.
* Link para o Swagger (`<URL do gateway>/apidocs/`) e para os deploys ativos nos READMEs.
* Diagramas de componentes e de sequência exportados e com link de visualização.
