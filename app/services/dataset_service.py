import unittest
from typing import List

from app.repository.dataset_repository import DatasetRepository
from app.exceptions import DatasetInvalidoError, DatasetDuplicadoError
from werkzeug.datastructures import FileStorage
from app.utils import validate_csv_content  # corrigido
import traceback

from app.exceptions import ResourceNotFoundError
from app.models import Dataset


class DatasetService:
    def __init__(self):
        self.repository = DatasetRepository()

    def create_dataset(self, limit_col: str, file_storage:FileStorage) -> Dataset:
        try:
            if not limit_col or len(limit_col) != 1:
                raise DatasetInvalidoError("Separador deve ser um único caractere")
            if not file_storage or not file_storage.filename:
                raise DatasetInvalidoError("Arquivo é obrigatório")

            name = file_storage.filename

            # Lê conteúdo
            file_content = file_storage.read()

            # Valida CSV
            valid, message = validate_csv_content(file_content, limit_col)
            if not valid:
                raise DatasetInvalidoError(f"CSV inválido: {message}")

            dataset = Dataset(
                name=name,
                limit_col=limit_col,
                file_content=file_content,
                file_size=len(file_content)  # tamanho em bytes
            )

            # Salva no banco
            return self.repository.save(dataset)

        except DatasetInvalidoError:
            raise
        except Exception as e:
            print("=" * 60)
            print("ERRO NO SERVICE:")
            traceback.print_exc()
            print("=" * 60)
            # Lança uma RuntimeError com a mensagem original
            raise RuntimeError(f"Falha ao processar dataset: {str(e)}") from e

    def list_datasets(self) -> List[Dataset]:
        return self.repository.find_all()

    def get_by_id(self, dataset_id: int) -> Dataset:
        dataset_response = self.repository.find_by_id(dataset_id)
        if dataset_response is None:
            raise ResourceNotFoundError("O dataset não foi encontrado!")
        return dataset_response

    def remove_dataset(self, dataset_id: int) ->bool:
        dataset = self.repository.find_by_id(dataset_id)
        if dataset:
            self.repository.delete(dataset)
            return True  # Ação executada com sucesso

        raise ResourceNotFoundError("O dataset não foi encontrado!")

    if __name__ == '__main__':
        unittest.main()