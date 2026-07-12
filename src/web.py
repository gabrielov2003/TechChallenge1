import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from application import OficinaAppService
from flasgger import swag_from

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Login'],
    'description': 'Rota para fazer login e retornar o Bearer Token'
})
def login():
    data = request.json or {}
    username = data.get('username')
    senha = data.get('senha')
    if not username or not senha:
        return jsonify({"erro": "username e senha são obrigatórios"}), 400
    user_id = OficinaAppService.autenticar_usuario(username, senha)
    if not user_id:
        return jsonify({"erro": "Credenciais inválidas"}), 401
    token = create_access_token(identity=user_id)
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
    resultado = OficinaAppService.abrir_ordem_servico(
        data['id_cliente'], data['id_veiculo'],
        pecas=data.get('pecas'), servicos=data.get('servicos')
    )

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
    resultado = OficinaAppService.buscar_cliente_por_documento(doc)
    if not resultado:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify(resultado), 200


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
    resultado = OficinaAppService.buscar_veiculo_por_placa(placa)
    if not resultado:
        return jsonify({"erro": "Veiculo não encontrado"}), 404
    return jsonify(resultado), 200


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
    if resultado is False:
        return jsonify({"erro": "OS não encontrada ou transição inválida"}), 400

    return jsonify({"mensagem": "Status atualizado"}), 200


@api.route('/os/<int:id_os>/status', methods=['GET'])
def get_os_status(id_os):
    resultado = OficinaAppService.gerar_orcamento_consolidado(id_os)
    if not resultado:
        return jsonify({"erro": "OS não encontrada"}), 404
    return jsonify({"id_os": id_os, "status": resultado["status"]}), 200


@api.route('/os/<int:id_os>/aprovacao', methods=['POST'])
@jwt_required()
def aprovar_orcamento(id_os):
    data = request.json or {}
    if 'aprovado' not in data:
        return jsonify({"erro": "'aprovado' é obrigatório"}), 400
    resultado = OficinaAppService.aprovar_orcamento(id_os, data['aprovado'])
    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400
    acao = "aprovado" if data['aprovado'] else "recusado"
    return jsonify({"mensagem": f"Orçamento {acao}"}), 200


@api.route('/os/webhook/status', methods=['POST'])
def webhook_status():
    token = request.headers.get('X-Webhook-Token') or (request.json or {}).get('token')
    if token != os.getenv('WEBHOOK_TOKEN', 'webhook-secret'):
        return jsonify({"erro": "Token inválido"}), 401
    data = request.json or {}
    id_os = data.get('id_os')
    novo_status = data.get('status')
    if not id_os or not novo_status:
        return jsonify({"erro": "id_os e status são obrigatórios"}), 400
    resultado = OficinaAppService.atualizar_progresso_os(id_os, novo_status)
    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400
    if resultado is False:
        return jsonify({"erro": "OS não encontrada ou transição inválida"}), 400
    return jsonify({"mensagem": "Status atualizado"}), 200


@api.route('/os', methods=['GET'])
@jwt_required()
def listar_os():
    return jsonify(OficinaAppService.listar_ordens()), 200


@api.route('/os/tempo-medio', methods=['GET'])
@jwt_required()
def tempo_medio_os():
    media = OficinaAppService.tempo_medio_execucao()
    return jsonify({"media_dias": media}), 200


@api.route('/clientes', methods=['GET'])
@jwt_required()
def listar_clientes():
    return jsonify(OficinaAppService.listar_clientes()), 200


@api.route('/clientes/<int:id_cliente>', methods=['GET'])
@jwt_required()
def get_cliente(id_cliente):
    c = OficinaAppService.buscar_cliente_por_id(id_cliente)
    if not c:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify(c), 200


@api.route('/clientes/<int:id_cliente>', methods=['PUT'])
@jwt_required()
def put_cliente(id_cliente):
    data = request.json
    resultado = OficinaAppService.atualizar_cliente(id_cliente, data['nome'], data['documento'])
    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400
    if not resultado:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify({"mensagem": "Cliente atualizado"}), 200


@api.route('/clientes/<int:id_cliente>', methods=['DELETE'])
@jwt_required()
def delete_cliente(id_cliente):
    if not OficinaAppService.deletar_cliente(id_cliente):
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify({"mensagem": "Cliente removido"}), 200


@api.route('/veiculos', methods=['GET'])
@jwt_required()
def listar_veiculos():
    return jsonify(OficinaAppService.listar_veiculos()), 200


@api.route('/veiculos/<int:id_veiculo>', methods=['GET'])
@jwt_required()
def get_veiculo(id_veiculo):
    v = OficinaAppService.buscar_veiculo_por_id(id_veiculo)
    if not v:
        return jsonify({"erro": "Veículo não encontrado"}), 404
    return jsonify(v), 200


@api.route('/veiculos/<int:id_veiculo>', methods=['PUT'])
@jwt_required()
def put_veiculo(id_veiculo):
    data = request.json
    resultado = OficinaAppService.atualizar_veiculo(
        id_veiculo, data['placa'], data['marca'], data['modelo'], data['ano']
    )
    if isinstance(resultado, dict) and "erro" in resultado:
        return jsonify(resultado), 400
    if not resultado:
        return jsonify({"erro": "Veículo não encontrado"}), 404
    return jsonify({"mensagem": "Veículo atualizado"}), 200


@api.route('/veiculos/<int:id_veiculo>', methods=['DELETE'])
@jwt_required()
def delete_veiculo(id_veiculo):
    if not OficinaAppService.deletar_veiculo(id_veiculo):
        return jsonify({"erro": "Veículo não encontrado"}), 404
    return jsonify({"mensagem": "Veículo removido"}), 200


@api.route('/pecas', methods=['POST'])
@jwt_required()
def post_peca():
    data = request.json
    resultado = OficinaAppService.cadastrar_peca(
        data['nome'], data['valor_unitario'], data.get('estoque', 0)
    )
    return jsonify({"id_peca": resultado}), 201


@api.route('/pecas', methods=['GET'])
@jwt_required()
def listar_pecas():
    return jsonify(OficinaAppService.listar_pecas()), 200


@api.route('/pecas/<int:id_peca>', methods=['GET'])
@jwt_required()
def get_peca(id_peca):
    p = OficinaAppService.buscar_peca_por_id(id_peca)
    if not p:
        return jsonify({"erro": "Peça não encontrada"}), 404
    return jsonify(p), 200


@api.route('/pecas/<int:id_peca>', methods=['PUT'])
@jwt_required()
def put_peca(id_peca):
    data = request.json
    if not OficinaAppService.atualizar_peca(id_peca, data['nome'], data['valor_unitario'], data['estoque']):
        return jsonify({"erro": "Peça não encontrada"}), 404
    return jsonify({"mensagem": "Peça atualizada"}), 200


@api.route('/pecas/<int:id_peca>', methods=['DELETE'])
@jwt_required()
def delete_peca(id_peca):
    if not OficinaAppService.deletar_peca(id_peca):
        return jsonify({"erro": "Peça não encontrada"}), 404
    return jsonify({"mensagem": "Peça removida"}), 200


@api.route('/servicos', methods=['POST'])
@jwt_required()
def post_servico():
    data = request.json
    resultado = OficinaAppService.cadastrar_servico_catalogo(data['nome'], data['valor'])
    return jsonify({"id_servico": resultado}), 201


@api.route('/servicos', methods=['GET'])
@jwt_required()
def listar_servicos():
    return jsonify(OficinaAppService.listar_servicos_catalogo()), 200


@api.route('/servicos/<int:id_servico>', methods=['GET'])
@jwt_required()
def get_servico(id_servico):
    s = OficinaAppService.buscar_servico_por_id(id_servico)
    if not s:
        return jsonify({"erro": "Serviço não encontrado"}), 404
    return jsonify(s), 200


@api.route('/servicos/<int:id_servico>', methods=['PUT'])
@jwt_required()
def put_servico(id_servico):
    data = request.json
    if not OficinaAppService.atualizar_servico(id_servico, data['nome'], data['valor']):
        return jsonify({"erro": "Serviço não encontrado"}), 404
    return jsonify({"mensagem": "Serviço atualizado"}), 200


@api.route('/servicos/<int:id_servico>', methods=['DELETE'])
@jwt_required()
def delete_servico(id_servico):
    if not OficinaAppService.deletar_servico(id_servico):
        return jsonify({"erro": "Serviço não encontrado"}), 404
    return jsonify({"mensagem": "Serviço removido"}), 200