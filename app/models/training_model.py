from numpy.f2py.symbolic import Language

from app.extensions import db
from enum import Enum
import datetime

class TrainingStatus(str, Enum):
    PENDING = "PENDING"       # Aguardando na fila (opcional)
    PROCESSING = "PROCESSING" # Treinamento em andamento
    COMPLETED = "COMPLETED"   # Concluído com sucesso
    FAILED = "FAILED"         # Ocorreu algum erro/parada (antigo 'STOP')

class VectorizerType(str, Enum):
    TF_IDF = "TF_IDF"
    BAG_OF_WORDS = "BAG_OF_WORDS"
    WORD2VEC = "WORD2VEC"

class Training(db.Model):
    __tablename__ = 'training_status'
    __table_args__ = {'extend_existing': True}
    # Chave Primária com Auto Incremento automático
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Chave Estrangeira apontando para a tabela 'dataset'
    id_dataset = db.Column(db.Integer, db.ForeignKey('dataset.id', ondelete='CASCADE'), nullable=False)

    # Status do treinamento (Não nulo)
    #status = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(TrainingStatus), nullable=False, default=TrainingStatus.PROCESSING)

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
    #dataset = db.relationship('Dataset', backref=db.backref('trainings', lazy=True, cascade="all, delete"))
    #dataset = db.relationship('app.models.Dataset', backref=db.backref('trainings', lazy=True, cascade="all, delete"))

    dataset = db.relationship('app.models.dataset_model.Dataset', back_populates='trainings')

    #Guardar o modelo de treinamento no banco
    trained_model = db.Column(db.LargeBinary, nullable=True)

    #Guardar a vetorização do dataframe para usar na classificação
    vectorizer = db.Column(db.LargeBinary, nullable=True)

    # Novas colunas mapeadas do banco:
    vectorizer_type = db.Column(
        db.Enum(VectorizerType),
        nullable=False,
        default=VectorizerType.TF_IDF
    )

    use_stemmer = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    language = db.Column(
        db.String(50),
        nullable=False,
        default='portuguese'

    )

    def to_dict(self):
        """Método auxiliar para quando você precisar retornar isso no Controller"""
        return {
            'id': self.id,
            'id_dataset': self.id_dataset,
            'status': self.status.value,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'precision': float(self.precision) if self.precision else None,
            'recall': float(self.recall) if self.recall else None,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'cross_val_score_mean': float(self.cross_val_score_mean) if self.cross_val_score_mean else None,
            'vectorizer_type': self.vectorizer_type.value,  # Retorna a string pura
            'use_stemmer': self.use_stemmer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }