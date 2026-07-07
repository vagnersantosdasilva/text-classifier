# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env (opcional, pode ser feito no __init__)

class Config:
    # Configuração do banco de dados
    SGBD = os.getenv('SGBD', 'mysql+mysqlconnector')
    DB_USER = os.getenv('DB_USER', 'estudo')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'classificador')
    SQLALCHEMY_DATABASE_URI = f'{SGBD}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limite de tamanho de upload (ex: 100 MB)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # Outras configurações podem ser adicionadas aqui
    # SECRET_KEY, etc.

    TRAINING_MAX_WORKERS = int(os.getenv('TRAINING_MAX_WORKERS', '2'))

    # Limite de treinamentos simultâneos ativos POR DATASET (Regra de negócio)
    MAX_ACTIVE_TRAININGS_PER_DATASET = int(os.getenv('MAX_ACTIVE_TRAININGS_PER_DATASET', '2'))
