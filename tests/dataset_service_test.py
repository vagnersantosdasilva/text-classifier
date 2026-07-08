# tests/test_dataset_service.py
import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services import DatasetService
from app.exceptions import DatasetInvalidoError, ResourceNotFoundError
from app.models import Dataset


class TestDatasetService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        # Patch para injetar o repositório mockado diretamente no serviço
        with patch('app.services.dataset_service.DatasetRepository', return_value=self.mock_repo):
            self.service = DatasetService()

    def test_create_dataset_success(self):
        """Garante a criação bem sucedida do dataset quando o CSV é válido"""
        # Cria um arquivo falso em memória simulando o upload de um CSV
        csv_data = b"description;priority\nErro no banco;ALTA"
        file_storage = FileStorage(stream=BytesIO(csv_data), filename="dados.csv")

        # Simula o retorno do banco de dados
        expected_dataset = Dataset(id=1, name="dados.csv", limit_col=";")
        self.mock_repo.save.return_value = expected_dataset

        with patch('app.services.dataset_service.validate_csv_content', return_value=(True, "Válido")):
            result = self.service.create_dataset(limit_col=";", file_storage=file_storage)

            self.assertEqual(result.id, 1)
            self.assertEqual(result.name, "dados.csv")
            self.mock_repo.save.assert_called_once()

    def test_create_dataset_invalid_separator(self):
        """Deve disparar DatasetInvalidoError se o separador tiver tamanho inválido"""
        file_storage = FileStorage(stream=BytesIO(b""), filename="test.csv")

        with self.assertRaises(DatasetInvalidoError):
            self.service.create_dataset(limit_col="INVALIDO", file_storage=file_storage)

    def test_get_by_id_not_found(self):
        """Deve disparar ResourceNotFoundError se o ID do dataset não existir"""
        self.mock_repo.find_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundError):
            self.service.get_by_id(999)


if __name__ == '__main__':
    unittest.main()