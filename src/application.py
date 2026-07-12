from infrastructure import Infrastructure
from domain import Cliente, Veiculo, OrdemServico, DomainError, PecasCarro, ServicosCarro, Usuario, STATUS_FLUXO


class OficinaAppService:
    @staticmethod
    def autenticar_usuario(username, senha):
        row = Infrastructure.fetch_one(
            "SELECT id_usuario, username, senha_hash FROM Usuario WHERE username = ?", (username,)
        )
        if not row:
            return None
        u = Usuario(username=row['username'], senha_hash=row['senha_hash'], id_usuario=row['id_usuario'])
        return str(u.id_usuario) if u.verificar_senha(senha) else None

    @staticmethod
    def cadastrar_cliente(nome, documento):
        try:
            novo_cliente = Cliente(documento=documento, nome=nome)

            query = "INSERT INTO Cliente (nome, documento) VALUES (?, ?)"
            return Infrastructure.execute_query(query, (novo_cliente.nome, novo_cliente.documento))
        except DomainError as e:
            return {"erro": str(e)}

    @staticmethod
    def listar_clientes():
        return Infrastructure.fetch_pandas("SELECT * FROM Cliente").to_dict(orient='records')

    @staticmethod
    def buscar_cliente_por_id(id_cliente):
        return Infrastructure.fetch_one("SELECT * FROM Cliente WHERE id_cliente = ?", (id_cliente,))

    @staticmethod
    def buscar_cliente_por_documento(documento):
        return Infrastructure.fetch_pandas(
            "SELECT * FROM Cliente WHERE documento = ?", (documento,)
        ).to_dict(orient='records')

    @staticmethod
    def atualizar_cliente(id_cliente, nome, documento):
        try:
            c = Cliente(documento=documento, nome=nome)
            rows = Infrastructure.execute_update(
                "UPDATE Cliente SET nome = ?, documento = ? WHERE id_cliente = ?",
                (c.nome, c.documento, id_cliente)
            )
            return rows > 0
        except DomainError as e:
            return {"erro": str(e)}

    @staticmethod
    def deletar_cliente(id_cliente):
        return Infrastructure.execute_update(
            "DELETE FROM Cliente WHERE id_cliente = ?", (id_cliente,)
        ) > 0

    @staticmethod
    def listar_veiculos():
        return Infrastructure.fetch_pandas("SELECT * FROM Veiculo").to_dict(orient='records')

    @staticmethod
    def buscar_veiculo_por_id(id_veiculo):
        return Infrastructure.fetch_one("SELECT * FROM Veiculo WHERE id_veiculo = ?", (id_veiculo,))

    @staticmethod
    def buscar_veiculo_por_placa(placa):
        return Infrastructure.fetch_pandas(
            "SELECT * FROM Veiculo WHERE placa = ?", (placa,)
        ).to_dict(orient='records')

    @staticmethod
    def atualizar_veiculo(id_veiculo, placa, marca, modelo, ano):
        try:
            v = Veiculo(placa=placa, marca=marca, modelo=modelo, ano=ano)
            rows = Infrastructure.execute_update(
                "UPDATE Veiculo SET placa = ?, marca = ?, modelo = ?, ano = ? WHERE id_veiculo = ?",
                (v.placa, v.marca, v.modelo, v.ano, id_veiculo)
            )
            return rows > 0
        except DomainError as e:
            return {"erro": str(e)}

    @staticmethod
    def deletar_veiculo(id_veiculo):
        return Infrastructure.execute_update(
            "DELETE FROM Veiculo WHERE id_veiculo = ?", (id_veiculo,)
        ) > 0

    @staticmethod
    def cadastrar_peca(nome, valor_unitario, estoque=0):
        return Infrastructure.execute_query(
            "INSERT INTO Peca (nome, valor_unitario, estoque) VALUES (?, ?, ?)",
            (nome, float(valor_unitario), int(estoque))
        )

    @staticmethod
    def listar_pecas():
        return Infrastructure.fetch_pandas("SELECT * FROM Peca").to_dict(orient='records')

    @staticmethod
    def buscar_peca_por_id(id_peca):
        return Infrastructure.fetch_one("SELECT * FROM Peca WHERE id_peca = ?", (id_peca,))

    @staticmethod
    def atualizar_peca(id_peca, nome, valor_unitario, estoque):
        return Infrastructure.execute_update(
            "UPDATE Peca SET nome = ?, valor_unitario = ?, estoque = ? WHERE id_peca = ?",
            (nome, float(valor_unitario), int(estoque), id_peca)
        ) > 0

    @staticmethod
    def deletar_peca(id_peca):
        return Infrastructure.execute_update("DELETE FROM Peca WHERE id_peca = ?", (id_peca,)) > 0

    @staticmethod
    def cadastrar_servico_catalogo(nome, valor):
        return Infrastructure.execute_query(
            "INSERT INTO Servico (nome, valor) VALUES (?, ?)", (nome, float(valor))
        )

    @staticmethod
    def listar_servicos_catalogo():
        return Infrastructure.fetch_pandas("SELECT * FROM Servico").to_dict(orient='records')

    @staticmethod
    def buscar_servico_por_id(id_servico):
        return Infrastructure.fetch_one("SELECT * FROM Servico WHERE id_servico = ?", (id_servico,))

    @staticmethod
    def atualizar_servico(id_servico, nome, valor):
        return Infrastructure.execute_update(
            "UPDATE Servico SET nome = ?, valor = ? WHERE id_servico = ?",
            (nome, float(valor), id_servico)
        ) > 0

    @staticmethod
    def deletar_servico(id_servico):
        return Infrastructure.execute_update(
            "DELETE FROM Servico WHERE id_servico = ?", (id_servico,)
        ) > 0

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
    def abrir_ordem_servico(id_cliente, id_veiculo, pecas=None, servicos=None):
        os_dominio = OrdemServico(id_cliente=id_cliente, id_veiculo=id_veiculo)

        query = "INSERT INTO Ordem_Servico (id_cliente, id_veiculo, status) VALUES (?, ?, ?)"
        id_os = Infrastructure.execute_query(query, (os_dominio.id_cliente, os_dominio.id_veiculo,
                                                     os_dominio.status))
        for p in (pecas or []):
            OficinaAppService.adicionar_peca(id_os, p['peca'], p['valor_total'])
        for s in (servicos or []):
            OficinaAppService.adicionar_servico(id_os, s['servico'], s['valor_total'])
        return id_os

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
    def listar_ordens():
        query = """
            SELECT * FROM Ordem_Servico
            WHERE status NOT IN ('Finalizada', 'Entregue', 'Recusada')
            ORDER BY CASE status
                WHEN 'Em execução' THEN 1
                WHEN 'Aguardando aprovação' THEN 2
                WHEN 'Em diagnóstico' THEN 3
                WHEN 'Recebida' THEN 4
                ELSE 5
            END, data_abertura ASC
        """
        return Infrastructure.fetch_pandas(query).to_dict(orient='records')

    @staticmethod
    def aprovar_orcamento(id_os, aprovado):
        row = Infrastructure.fetch_one("SELECT status FROM Ordem_Servico WHERE id_os = ?", (id_os,))
        if not row:
            return {"erro": "OS não encontrada"}
        if row['status'] != "Aguardando aprovação":
            return {"erro": f"OS não está aguardando aprovação (status atual: '{row['status']}')"}
        if aprovado:
            return OficinaAppService.atualizar_progresso_os(id_os, "Em execução")
        Infrastructure.execute_query(
            "UPDATE Ordem_Servico SET status = ? WHERE id_os = ?", ("Recusada", id_os)
        )
        return True

    @staticmethod
    def tempo_medio_execucao():
        row = Infrastructure.fetch_one(
            "SELECT AVG(julianday(data_fechamento) - julianday(data_abertura)) AS media_dias "
            "FROM Ordem_Servico WHERE data_fechamento IS NOT NULL"
        )
        return row['media_dias'] if row else None

    @staticmethod
    def atualizar_progresso_os(id_os, novo_status):
        row = Infrastructure.fetch_one("SELECT status FROM Ordem_Servico WHERE id_os = ?", (id_os,))
        if not row:
            return False
        os_obj = OrdemServico(0, 0, id_os=id_os, status=row['status'])
        if not os_obj.pode_transicionar_para(novo_status):
            return {"erro": f"Transição inválida de '{row['status']}' para '{novo_status}'"}
        extra = ""
        params = [novo_status]
        if novo_status == "Entregue":
            extra = ", data_fechamento = CURRENT_TIMESTAMP"
        params.append(id_os)
        Infrastructure.execute_query(
            f"UPDATE Ordem_Servico SET status = ?{extra} WHERE id_os = ?", tuple(params)
        )
        return True

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