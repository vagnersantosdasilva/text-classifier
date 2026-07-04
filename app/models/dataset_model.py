from app.extensions import db
import datetime

class Dataset(db.Model):
    __tablename__ = 'dataset'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit_col = db.Column(db.String(5), nullable=False)
    file_content = db.Column(db.LargeBinary, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # RELACIONAMENTO FIXADO: Usando o caminho absoluto do módulo em string
    #trainings = db.relationship('app.models.Training', back_populates='dataset', cascade="all, delete")
    trainings = db.relationship(
        'app.models.training_model.Training',
        back_populates='dataset',
        cascade="all, delete"
    )


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

