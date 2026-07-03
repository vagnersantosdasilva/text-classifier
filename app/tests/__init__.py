# test_db.py
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    try:
        db.engine.connect()
        print("Conexão OK")
    except Exception as e:
        print(f"Erro: {e}")