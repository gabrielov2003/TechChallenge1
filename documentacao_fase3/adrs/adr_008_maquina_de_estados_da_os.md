# ADR 008: Máquina de estados da OS com transição atômica e histórico

Data: 13/09/2026

Status: Aceita

## Contexto

O status de uma ordem de serviço pode ser alterado por três origens: o funcionário, o próprio cliente, na aprovação do orçamento, e sistemas externos, pelo webhook. Na Fase 2 o status era sobrescrito sem registro das etapas anteriores, o que impedia medir o tempo gasto em cada etapa, pedido no dashboard da Fase 3. Também não havia proteção contra duas alterações simultâneas na mesma OS. Com várias réplicas da API ([ADR 002](adr_002_escalabilidade_com_hpa.md)), essas alterações simultâneas passam a ser possíveis na prática.

## Decisão

Mantemos as transições permitidas no domínio, no dicionário `TRANSICOES` de `domain.py`. Uma OS "Recebida" vai para "Em diagnóstico", que vai para "Aguardando aprovação". De "Aguardando aprovação", ela pode ir para "Aprovado", "Recusada" ou "Solicitado alterações", e "Solicitado alterações" volta para "Em diagnóstico". "Aprovado" segue para "Em execução" ou "Aguardando peças", e "Aguardando peças" segue para "Em execução" ou "Recusada". "Em execução" vai para "Finalizada", "Finalizada" vai para "Entregue", e "Recusada" e "Entregue" são estados finais.

Toda mudança de status passa pelo mesmo caso de uso, que valida a transição no domínio antes de gravar, venha ela do funcionário, do cliente ou do webhook. A gravação é condicional: o `UPDATE` só altera a linha se o status no banco ainda for o status lido. Se outra requisição mudou o status nesse intervalo, nenhuma linha é afetada e a operação é recusada, sem sobrescrever o que já foi gravado.

Na mesma transação, a aplicação calcula quanto tempo a OS ficou no status anterior e grava uma linha em `historico_status_os`. A data de fechamento é gravada quando a OS chega a "Entregue". Cada mudança emite as métricas `oficina.os.status_alterado` e `oficina.os.tempo_status`, e cada transição rejeitada gera o log `transicao_rejeitada`. As falhas inesperadas passam pelo decorator `monitorar_os`, que registra o log com a stack e incrementa `oficina.os.falhas`, a métrica que alimenta o alerta de falhas.

## Consequências

### Positivas

* Nenhuma transição fora do fluxo chega ao banco, qualquer que seja a origem.
* Duas alterações simultâneas não se sobrescrevem.
* O histórico permite calcular o tempo médio por status, tanto no banco quanto no dashboard.

### Negativas

* O conjunto de status válidos é garantido pelo domínio, e não por uma restrição no banco. Uma evolução é criar uma tabela de status ou um CHECK com a lista.
* Uma requisição recusada por concorrência precisa ser repetida por quem chamou a API.

## Alternativas consideradas

* Lock pessimista com `SELECT ... FOR UPDATE`: funcionaria, mas mantém a linha travada durante a validação. A gravação condicional resolve com uma instrução só.
* Guardar só o status atual e calcular os tempos pelos logs: descartado por ser frágil e depender da retenção dos logs.
* Validar as transições com CHECK ou trigger no banco: descartado porque espalharia a regra de negócio entre o domínio e o banco.
