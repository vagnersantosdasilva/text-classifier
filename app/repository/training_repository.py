from typing import Optional, List

from sqlalchemy import or_

from app.extensions import db
from app.models import Training
from app.models import TrainingStatus


class TrainingRepository:
    def __init__(self):
        self.model = Training


    def save(self, training: Training) -> Training:
        db.session.add(training)
        db.session.commit()
        db.session.refresh(training)  # atualiza a instância com valores gerados
        return training


    def find_by_id(self, training_id: int) -> Optional[Training]:
        return self.model.query.get(training_id)


    def find_by_dataset_id(self, dataset_id: int) -> List[Training]:
        return Training.query.filter(Training.id_dataset == dataset_id).all()


    def count_active_by_dataset(self, dataset_id: int) -> int:
        return Training.query.filter(
            Training.id_dataset == dataset_id,
            or_(
                Training.status == TrainingStatus.PROCESSING,
                Training.status == TrainingStatus.PENDING
            )
        ).count()


    def find_all(self) -> List[Training]:
        return self.model.query.all()


    def delete(self, training: Training) -> None:
        db.session.delete(training)
        db.session.commit()


    def delete_by_id(self, training_id: int) -> bool:
        training = self.find_by_id(training_id)
        if training:
            self.delete(training)
            return True
        return False


    def count(self) -> int:
        return self.model.query.count()
