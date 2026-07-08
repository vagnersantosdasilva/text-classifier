# tests/test_classifier_service.py
import unittest
from unittest.mock import MagicMock, patch
import pickle
from app.services import ClassifierService
from app.models import Classe, TrainingStatus
from app.exceptions import TreinamentoError, ResourceNotFoundError


class TestClassifierService(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        with patch('app.services.classifier_service.TrainingRepository', return_value=self.mock_repo):
            self.service = ClassifierService()

    def test_classify_message_empty_string(self):
        """Strings vazias ou nulas não devem chamar o banco e devem retornar INDETERMINADA"""
        input_data = Classe(id_training=1, message="   ")
        response = self.service.classify_message(input_data)

        self.assertEqual(response.classe, "INDETERMINADA")
        self.mock_repo.find_by_id.assert_not_called()

    @patch('app.services.classifier_service.pickle.loads')
    def test_classify_message_success(self, mock_pickle_loads):
        """Sucesso ao deserializar o pipeline e classificar a mensagem de entrada"""
        input_classe = Classe(id_training=1, message="Mensagem válida de teste")

        # Cria mocks que mimetizam o comportamento do scikit-learn e do strategy
        mock_training = MagicMock()
        mock_training.status = TrainingStatus.COMPLETED
        mock_training.trained_model = b"bytes_modelo"
        mock_training.vectorizer = b"bytes_vetorizador"
        self.mock_repo.find_by_id.return_value = mock_training

        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = ['1']  # Array numpy simulado contendo a classe '1'
        mock_strategy = MagicMock()
        mock_strategy.transform.return_value = "matriz_esparsa_simulada"

        # O primeiro loads retorna o predictor, o segundo retorna o strategy
        mock_pickle_loads.side_effect = [mock_predictor, mock_strategy]

        result = self.service.classify_message(input_classe)

        self.assertEqual(result.classe, "1")
        mock_strategy.transform.assert_called_once_with(["Mensagem válida de teste"])
        mock_predictor.predict.assert_called_once_with("matriz_esparsa_simulada")

    def test_classify_message_training_not_completed(self):
        """Deve estourar erro se o status do treinamento for PROCESSING ou FAILED"""
        input_classe = Classe(id_training=1, message="Teste")
        mock_training = MagicMock()
        mock_training.status = TrainingStatus.PROCESSING
        self.mock_repo.find_by_id.return_value = mock_training

        with self.assertRaises(TreinamentoError):
            self.service.classify_message(input_classe)

if __name__ == '__main__':
    unittest.main()