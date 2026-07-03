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
        db.session.refresh(dataset)  # atualiza a instância com valores gerados (ex: id)
        return dataset

    def find_by_id(self, dataset_id: int) -> Optional[Dataset]:
        """Busca um dataset pelo ID."""
        return self.model.query.get(dataset_id)

    def find_by_name(self, name: str) -> Optional[Dataset]:
        """Busca um dataset pelo nome (exato)."""
        return self.model.query.filter_by(name=name).first()

    def find_all(self) -> List[Dataset]:
        """Retorna todos os datasets."""
        return self.model.query.all()

    def find_by_name_like(self, name_pattern: str) -> List[Dataset]:
        """Busca datasets cujo nome contém um padrão (case-insensitive)."""
        return self.model.query.filter(self.model.name.ilike(f'%{name_pattern}%')).all()

    def delete(self, dataset: Dataset) -> None:
        """Remove um dataset do banco."""
        db.session.delete(dataset)
        db.session.commit()

    def delete_by_id(self, dataset_id: int) -> bool:
        """Remove um dataset pelo ID. Retorna True se removido, False se não encontrado."""
        dataset = self.find_by_id(dataset_id)
        if dataset:
            self.delete(dataset)
            return True
        return False

    def exists_by_name(self, name: str) -> bool:
        """Verifica se já existe um dataset com o nome fornecido."""
        return self.model.query.filter_by(name=name).first() is not None

    def count(self) -> int:
        """Retorna o número total de datasets."""
        return self.model.query.count()