# app/__init__.py
from flask import Flask
from app.extensions import db
#from dotenv import load_dotenv
#import os

#load_dotenv()  # Carrega variáveis do .env para o ambiente


def create_app():
    app = Flask(__name__)

    # Carrega configurações do objeto Config
    from app.config import Config
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)

    # Registra blueprints (importação local para evitar circular)
    from app.controlls import dataset_bp
    app.register_blueprint(dataset_bp)

    with app.app_context():
        db.create_all()

    return app