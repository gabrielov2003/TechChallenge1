from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from application import OficinaAppService
from flasgger import swag_from
from infrastructure import Infrastructure

api = Blueprint('api', __name__)

@api.route('/login')
@swag_from({
    'tags': ['Login'],
    'description': 'Rota para fazer login e retornar o Berear Token, ele deve ser usado para fazer as proximas requisições'
})
def login():
    token = create_access_token(identity="1")
    return jsonify(access_token=token)

@api.route('/clientes', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Clientes'],
    'description': 'Cadastra um novo cliente no sistema',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['nome', 'documento'],
            'properties': {
                'nome': {'type': 'string', 'example': 'Gabriel Vieira'},
                'documento': {'type': 'string', 'example': '12345678901'}
            }
        }
    }],
    'responses': {
        201: {
            'description': 'Cliente criado com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'id_cliente': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': 'Erro de validação'}
    }
})
def post_cliente():
    data = request.json
    resultado = OficinaAppService.cadastrar_cliente(data['nome'], data['documento'])

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"id_cliente": resultado}), 201


@api.route('/veiculos', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Veículos'],
    'description': 'Cadastra um veículo',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['placa', 'marca', 'modelo', 'ano'],
            'properties': {
                'placa': {'type': 'string', 'example': 'ABC1D23'},
                'marca': {'type': 'string', 'example': 'Toyota'},
                'modelo': {'type': 'string', 'example': 'Corolla'},
                'ano': {'type': 'integer', 'example': 2022}
            }
        }
    }],
    'responses': {
        201: {'description': 'Veículo criado'},
        400: {'description': 'Erro de validação'}
    }
})
def post_veiculo():
    data = request.json
    resultado = OficinaAppService.cadastrar_veiculo(
        data['placa'], data['marca'], data['modelo'], data['ano']
    )

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"id_veiculo": resultado}), 201


@api.route('/os', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Ordem de Serviço'],
    'description': 'Cria uma nova ordem de serviço',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['id_cliente', 'id_veiculo'],
            'properties': {
                'id_cliente': {'type': 'integer', 'example': 1},
                'id_veiculo': {'type': 'integer', 'example': 2}
            }
        }
    }],
    'responses': {
        201: {'description': 'OS criada'},
        400: {'description': 'Erro'}
    }
})
def criar_os():
    data = request.json
    resultado = OficinaAppService.abrir_ordem_servico(data['id_cliente'], data['id_veiculo'])

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"id_os": resultado}), 201


@api.route('/clientes/documento/<doc>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Clientes'],
    'description': 'Busca cliente pelo CPF ou CNPJ',
    'parameters': [{
        'name': 'doc',
        'in': 'path',
        'type': 'string',
        'required': True,
        'example': '12345678901'
    }],
    'responses': {
        200: {'id_cliente': '456', 'documento': '123', 'nome': 'Gabriel'},
        404: {'description': 'Cliente não encontrado'}
    }
})
def get_cliente_por_documento(doc):
    query = "SELECT * FROM Clinete WHERE documento = ?"
    df = Infrastructure.fetch_pandas(query, (doc,))
    if df.empty:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify(df.to_dict(orient='records')), 200


@api.route('/veiculos/placa/<placa>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Veículos'],
    'description': 'Busca veiculo pela placa',
    'parameters': [{
        'name': 'placa',
        'in': 'path',
        'type': 'string',
        'required': True,
        'example': 'FSO9367'
    }],
    'responses': {
        200: {'id_veiculo': '456', 'placa': '123', 'marca': 'marca_x', 'movelo': 'modelo_y', 'ano': '2003'},
        404: {'description': 'Veiculo não encontrado'}
    }
})
def get_veiculo_por_placa(placa):
    query = "SELECT * FROM Veiculo WHERE placa = ?"
    df = Infrastructure.fetch_pandas(query, (placa,))
    if df.empty:
        return jsonify({"erro": "Veiculo não encontrado"}), 404
    return jsonify(df.to_dict(orient='records')), 200


@api.route('/os/<int:id_os>/servicos', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Ordem de Serviço'],
    'description': 'Adiciona um serviço a uma OS',
    'parameters': [
        {
            'name': 'id_os',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'example': 1
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['servico', 'valor_total'],
                'properties': {
                    'servico': {'type': 'string', 'example': 'Troca de óleo'},
                    'valor_total': {'type': 'number', 'example': 150.0}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Serviço adicionado'},
        400: {'description': 'Erro'}
    }
})
def adicionar_servico(id_os):
    data = request.json
    resultado = OficinaAppService.adicionar_servico(
        id_os, data['servico'], data['valor_total']
    )

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"mensagem": "Serviço adicionado"}), 201


@api.route('/os/<int:id_os>/pecas', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Ordem de Serviço'],
    'description': 'Adiciona uma peça a uma OS',
    'parameters': [
        {
            'name': 'id_os',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'example': 1
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['peca', 'valor_total'],
                'properties': {
                    'peca': {'type': 'string', 'example': 'Filtro de óleo'},
                    'valor_total': {'type': 'number', 'example': 80.0}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Peça adicionada'},
        400: {'description': 'Erro'}
    }
})
def adicionar_peca(id_os):
    data = request.json
    resultado = OficinaAppService.adicionar_peca(
        id_os, data['peca'], data['valor_total']
    )

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"mensagem": "Peça adicionada"}), 201


@api.route('/os/<int:id_os>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Ordem de Serviço'],
    'description': 'Retorna os dados completos da OS',
    'parameters': [{
        'name': 'id_os',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'example': 1
    }],
    'responses': {
        200: {'description': 'Dados da OS'},
        404: {'description': 'Não encontrada'}
    }
})
def get_os(id_os):
    resultado = OficinaAppService.gerar_orcamento_consolidado(id_os)

    if not resultado:
        return jsonify({"erro": "Ordem de Serviço não encontrada"}), 404

    return jsonify(resultado), 200


@api.route('/os/<int:id_os>/status', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Ordem de Serviço'],
    'description': 'Atualiza o status da OS',
    'parameters': [
        {
            'name': 'id_os',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'example': 1
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['status'],
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'Em execução'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Status atualizado'},
        400: {'description': 'Erro de validação'}
    }
})
def atualizar_status(id_os):
    data = request.json
    resultado = OficinaAppService.atualizar_progresso_os(id_os, data['status'])

    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400

    return jsonify({"mensagem": "Status atualizado"}), 200