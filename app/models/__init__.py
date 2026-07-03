import datetime

from app.extensions import db


class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit_col = db.Column(db.String(5), nullable=False)
    file_content = db.Column(db.LargeBinary, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'limit_col': self.limit_col,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat()
            # Evite colocar o 'file_content' aqui se ele for muito grande,
            # para não sobrecarregar a listagem.
        }


class Training(db.Model):
    __tablename__ = 'training_status'

    # Chave Primária com Auto Incremento automático
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Chave Estrangeira apontando para a tabela 'dataset'
    id_dataset = db.Column(db.Integer, db.ForeignKey('dataset.id', ondelete='CASCADE'), nullable=False)

    # Status do treinamento (Não nulo)
    status = db.Column(db.String(100), nullable=False)

    # Métricas usando Numeric/Decimal para bater com o decimal(5,4) do MySQL
    f1_score = db.Column(db.Numeric(precision=5, scale=4), nullable=True)
    precision = db.Column(db.Numeric(precision=5, scale=4), nullable=True)
    recall = db.Column(db.Numeric(precision=5, scale=4), nullable=True)
    accuracy_score = db.Column(db.Numeric(precision=5, scale=4), nullable=True)
    cross_val_score_mean = db.Column(db.Numeric(precision=5, scale=4), nullable=True)

    # Timestamps controlados pelo banco/SQLAlchemy
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Cria uma relação virtual para acessar o objeto Dataset direto do Training
    dataset = db.relationship('Dataset', backref=db.backref('trainings', lazy=True, cascade="all, delete"))

    def to_dict(self):
        """Método auxiliar para quando você precisar retornar isso no Controller"""
        return {
            'id': self.id,
            'id_dataset': self.id_dataset,
            'status': self.status,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'precision': float(self.precision) if self.precision else None,
            'recall': float(self.recall) if self.recall else None,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'cross_val_score_mean': float(self.cross_val_score_mean) if self.cross_val_score_mean else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Error:
    def __init__(self, message, code):
        self.message = message
        self.code = code


class Classifier:
    def __init__(self, predict=None, data_frame=None):
        self.predict = predict
        self.data_frame = data_frame
