# app/__init__.py
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)

    # Carrega configurações do objeto Config
    from app.config import Config
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)

    # Registra blueprints (importação local para evitar circular)
    from app.controllers import dataset_bp
    app.register_blueprint(dataset_bp)

    from app.controllers import data_training_bp
    app.register_blueprint(data_training_bp)

    from app.controllers import classifier_bp
    app.register_blueprint(classifier_bp)

    with app.app_context():
        db.create_all()

    return app