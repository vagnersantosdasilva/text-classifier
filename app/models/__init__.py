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

class Training:
    def __init__(self, id_dataset=None, status=None, id_training=None, f1_score=None, precision=None, recall=None,
                 accuracy_score=None , cross_val_score_mean=None):
        self.id = id_training
        self.status = status
        self.id_dataset = id_dataset
        self.f1_score = f1_score
        self.precision = precision
        self.recall = recall
        self.accuracy_score = accuracy_score
        self.cross_val_score_mean = cross_val_score_mean


class Error:
    def __init__(self, message, code):
        self.message = message
        self.code = code


class Classifier:
    def __init__(self, predict=None,  data_frame=None):
        self.predict = predict
        self.data_frame = data_frame
