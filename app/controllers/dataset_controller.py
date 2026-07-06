# app/controllers/dataset_controller.py

from flask import Blueprint, request, jsonify
from app.services.dataset_service import DatasetService
from app.exceptions import  AppException, ResourceNotFoundError


# Cria o Blueprint com prefixo /api/datasets
dataset_bp = Blueprint('dataset', __name__, url_prefix='/api/dataset')


@dataset_bp.route('/', methods=['POST'])
def upload_dataset():
    """
    Endpoint para enviar um arquivo CSV e criar um dataset.
    Espera multipart/form-data com os campos:
        - name (string)
        - separator (string, ex: ',')
        - file (arquivo)
    """
    try:
        # 1. Extrai os dados da requisição

        separator = request.form.get('separator')
        name = request.form.get('name')
        file = request.files['file_data']

        # 2. Validações básicas (o Service fará outras)
        if not file:
            return jsonify({"erro": "Nenhum arquivo enviado"}), 400

        # 3. Chama o Service para salvar
        service = DatasetService()
        dataset = service.create_dataset(
            separator,
            file
        )

        # 4. Retorna os metadados do dataset criado
        return jsonify({
            "id": dataset.id,
            'name': dataset.name,
            'limit_col': dataset.limit_col,
            'file_size': dataset.file_size,
            'created_at': dataset.created_at
        }), 201
    # except DatasetDuplicadoError as e:
    #     return jsonify(e.to_dict()), e.status_code
    except AppException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:  # Exceções inesperadas (ex: erro de banco)
        # Logar o erro
        return jsonify({"erro": "Erro interno no servidor"}), 500

    # URL final: GET /api/dataset/


@dataset_bp.route('/', methods=['GET'])
def get_all_datasets():
    try:
        service = DatasetService()
        datasets_objetos = service.list_datasets()

        # Converte a lista de objetos do banco para uma lista de dicionários
        datasets_json = [dataset.to_dict() for dataset in datasets_objetos]

        return jsonify(datasets_json), 200

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500



@dataset_bp.route('/<int:dataset_id>', methods=['GET'])
def get_dataset(dataset_id: int):
    try:
        service = DatasetService()
        dataset = service.get_by_id(dataset_id)
        return jsonify(dataset.to_dict()), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@dataset_bp.route('/<int:dataset_id>', methods=['DELETE'])
def remove_dataset(dataset_id: int):
    try:
        service = DatasetService()
        response = service.remove_dataset(dataset_id)
        return jsonify({"mensagem": f"Dataset com ID {dataset_id} deletado com sucesso."}), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500
