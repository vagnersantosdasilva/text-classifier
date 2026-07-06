from flask import Blueprint, jsonify, request
from app.services.data_training_service import DataTrainingService
from app.exceptions import ResourceNotFoundError

# Cria o Blueprint com prefixo /api/training
data_training_bp = Blueprint('data_training', __name__, url_prefix='/api')


@data_training_bp.route('/training/status/<int:training_id>', methods=['GET'])
def status(training_id):
    try:
        data_training_service = DataTrainingService()
        status = data_training_service.get_status_training(training_id)
        return jsonify({
            "id":training_id,
            "satus": status
        }), 200
    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500

@data_training_bp.route('/training', methods=['POST'])
def start_training():
    try:
        # Criação de um treinamento e retorno de status inicial ou mensagem de erro
        # 1. Captura o JSON enviado no body
        dados = request.get_json()

        # 2. Garante que o JSON não veio vazio e extrai o id_dataset
        if not dados or 'id_dataset' not in dados:
            return jsonify({"erro": "O campo 'id_dataset' é obrigatório no JSON"}), 400

        dataset_id = dados.get('id_dataset')
        data_training_service = DataTrainingService()
        training = data_training_service.create_training(dataset_id)
        return jsonify(training.to_dict()), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500

@data_training_bp.route('/training/<int:training_id>', methods=['GET'])
def get_training(training_id):
    try:
        training = DataTrainingService().get_training_by_id(training_id)
        return jsonify(training.to_dict()), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@data_training_bp.route('dataset/<int:dataset_id>/training', methods=['GET'])
def get_training_list(dataset_id):
    try:
        list_training = DataTrainingService().get_training_by_dataset(dataset_id)
        # Converte a lista de objetos do banco para uma lista de dicionários
        trainings_response = [training.to_dict() for training in list_training]

        return jsonify(trainings_response), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500