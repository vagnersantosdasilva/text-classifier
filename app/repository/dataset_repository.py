from app.extensions import db
from app.models import Dataset
from typing import Optional, List

class DatasetRepository:
    def __init__(self):
        self.model = Dataset

    def save(self, dataset: Dataset) -> Dataset:
        """Salva (insere ou atualiza) um dataset no banco."""
        db.session.add(dataset)
        db.session.commit()
        db.session.refresh(dataset)
        return dataset

    def find_by_id(self, dataset_id: int) -> Optional[Dataset]:
        return self.model.query.get(dataset_id)

    def find_by_name(self, name: str) -> Optional[Dataset]:
        return self.model.query.filter_by(name=name).first()

    def find_all(self) -> List[Dataset]:
        return self.model.query.all()

    def find_by_name_like(self, name_pattern: str) -> List[Dataset]:
        return self.model.query.filter(self.model.name.ilike(f'%{name_pattern}%')).all()

    def delete(self, dataset: Dataset) -> None:
        db.session.delete(dataset)
        db.session.commit()

    def delete_by_id(self, dataset_id: int) -> bool:
        dataset = self.find_by_id(dataset_id)
        if dataset:
            self.delete(dataset)
            return True
        return False

    def exists_by_name(self, name: str) -> bool:
        return self.model.query.filter_by(name=name).first() is not None

    def count(self) -> int:
        return self.model.query.count()