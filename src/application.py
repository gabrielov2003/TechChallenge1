from infrastructure import Infrastructure
from domain import Clinete, Veiculo, OrdemServico, DomainError, PecasCarro, ServicosCarro


class OficinaAppService:
    @staticmethod
    def cadastrar_cliente(nome, documento):
        try:
            novo_cliente = Clinete(documento=documento, nome=nome)

            query = "INSERT INTO Clinete (nome, documento) VALUES (?, ?)"
            return Infrastructure.execute_query(query, (novo_cliente.nome, novo_cliente.documento))
        except DomainError as e:
            return {"erro": str(e)}

    @staticmethod
    def cadastrar_veiculo(placa, marca, modelo, ano):
        try:
            novo_veiculo = Veiculo(placa=placa, marca=marca, modelo=modelo, ano=ano)

            query = "INSERT INTO Veiculo (placa, marca, modelo, ano) VALUES (?, ?, ?, ?)"
            return Infrastructure.execute_query(query, (novo_veiculo.placa, novo_veiculo.marca,
                                                        novo_veiculo.modelo, novo_veiculo.ano))
        except DomainError as e:
            return {"erro": str(e)}

    @staticmethod
    def abrir_ordem_servico(id_cliente, id_veiculo):
        os_dominio = OrdemServico(id_cliente=id_cliente, id_veiculo=id_veiculo)

        query = "INSERT INTO Ordem_Servico (id_cliente, id_veiculo, status) VALUES (?, ?, ?)"
        return Infrastructure.execute_query(query, (os_dominio.id_cliente, os_dominio.id_veiculo,
                                                    os_dominio.status))

    @staticmethod
    def adicionar_peca(id_os, nome_peca, valor):
        peca = PecasCarro(id_os=id_os, peca=nome_peca, valor_total=valor)

        query = "INSERT INTO Pecas_carro (id_os, peca, valor_total) VALUES (?, ?, ?)"
        return Infrastructure.execute_query(query, (peca.id_os, peca.peca, peca.valor_total))

    @staticmethod
    def adicionar_servico(id_os, nome_servico, valor):
        servico = ServicosCarro(id_os=id_os, servico=nome_servico, valor_total=valor)

        query = "INSERT INTO Servicos_carro (id_os, servico, valor_total) VALUES (?, ?, ?)"
        return Infrastructure.execute_query(query, (servico.id_os, servico.servico, servico.valor_total))

    @staticmethod
    def atualizar_progresso_os(id_os, novo_status):
        os_temp = OrdemServico(0, 0, id_os=id_os, status=novo_status)
        if novo_status in os_temp.STATUS_FLUXO:
            query = "UPDATE Ordem_Servico SET status = ? WHERE id_os = ?"
            Infrastructure.execute_query(query, (novo_status, id_os))
            return True
        return False

    @staticmethod
    def gerar_orcamento_consolidado(id_os):
        df_os = Infrastructure.fetch_pandas("SELECT * FROM Ordem_Servico WHERE id_os = ?", (id_os,))
        if df_os.empty:
            return None

        os_dominio = OrdemServico(id_cliente=int(df_os['id_cliente'][0]),
                                  id_veiculo=int(df_os['id_veiculo'][0]),
                                  id_os=id_os,
                                  status=df_os['status'][0])

        df_pecas = Infrastructure.fetch_pandas("SELECT * FROM Pecas_carro WHERE id_os = ?", (id_os,))
        df_servicos = Infrastructure.fetch_pandas("SELECT * FROM Servicos_carro WHERE id_os = ?", (id_os,))

        valor_total = 0.0
        pecas = []
        servicos = []

        for _, row in df_pecas.iterrows():
            pecas.append({'peca': row['peca'], 'valor_peca': row['valor_total'],})
            valor_total += row['valor_total']

        for _, row in df_servicos.iterrows():
            servicos.append({'servico': row['servico'], 'valor_servico': row['valor_total'], })
            valor_total += row['valor_total']

        return {
            "id_os": os_dominio.id_os,
            "id_veiculo": os_dominio.id_veiculo,
            "id_cliente": os_dominio.id_cliente,
            "status": os_dominio.status,
            "total_orcamento": valor_total,
            "detalhes": {
                "pecas": pecas,
                "servicos": servicos
            }
        }