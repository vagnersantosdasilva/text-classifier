from flask import Blueprint, request, jsonify
from app.services.data_training_service import DataTrainingService
from exceptions import ResourceNotFoundError

# Cria o Blueprint com prefixo /api/training
data_training_bp = Blueprint('data_training', __name__, url_prefix='/api/training')


@data_training_bp.route('/<int:dataset_id>', methods=['GET'])
def start_training(dataset_id: int):
    try:
        data_training_service = DataTrainingService()
        data_training_service.start_training(dataset_id)
        return jsonify({"teste":"teste"}), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500
