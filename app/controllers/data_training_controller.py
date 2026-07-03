from flask import Blueprint, request, jsonify
from app.services.data_training_service import DataTrainingService
from app.exceptions import DatasetInvalidoError, DatasetDuplicadoError, AppException

# Cria o Blueprint com prefixo /api/training
data_training_bp = Blueprint('data_training', __name__, url_prefix='/api/training')
