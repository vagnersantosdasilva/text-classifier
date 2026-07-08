# tests/test_data_training_service.py
import unittest
from unittest.mock import MagicMock, patch
from app import create_app
from app.services import DataTrainingService
from app.models import TrainingStatus, Dataset, Training
from app.exceptions import TreinamentoError


class TestDataTrainingService(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TRAINING_MAX_WORKERS'] = 2
        self.app.config['MAX_ACTIVE_TRAININGS_PER_DATASET'] = 1
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.mock_repo = MagicMock()
        self.mock_dataset_repo = MagicMock()

        with patch('app.services.data_training_service.TrainingRepository', return_value=self.mock_repo), \
                patch('app.services.data_training_service.DatasetRepository', return_value=self.mock_dataset_repo):
            self.service = DataTrainingService()

    def tearDown(self):
        self.app_context.pop()

    def test_create_training_limits_concurrency(self):
        """Garante que a regra de concorrência máxima de treinamentos ativos do mesmo dataset barre o fluxo"""
        mock_dataset = Dataset(id=1)
        self.mock_dataset_repo.find_by_id.return_value = mock_dataset
        self.mock_repo.count_active_by_dataset.return_value = 1

        with self.assertRaises(TreinamentoError) as context:
            self.service.create_training(dataset_id=1)

        self.assertIn("Limite de 1 treinamento(s) ativo(s)", str(context.exception))

    def test_create_training_triggers_thread_pool(self):
        """Garante que criar o treinamento joga o processamento assíncrono para o pool de threads"""
        mock_dataset = Dataset(id=1)
        self.mock_dataset_repo.find_by_id.return_value = mock_dataset
        self.mock_repo.count_active_by_dataset.return_value = 0

        expected_training = Training(id=5, id_dataset=1, status=TrainingStatus.PENDING)
        self.mock_repo.save.return_value = expected_training

        with patch.object(DataTrainingService, 'get_executor') as mock_get_executor:
            mock_executor = MagicMock()
            mock_get_executor.return_value = mock_executor

            self.service.create_training(dataset_id=1)

            mock_executor.submit.assert_called_once()
            args = mock_executor.submit.call_args[0]
            self.assertEqual(args[0], self.service.start_training)

    # CORREÇÃO 2: Substituído por dados numéricos balanceados o suficiente para cv=10
    def test_decide_training_with_small_sample(self):
        """Valida se o fluxo de avaliação estatística calcula as métricas numéricas corretas sem gerar NaN"""
        from sklearn.datasets import make_classification
        from sklearn.naive_bayes import GaussianNB

        # Geramos 120 amostras para garantir que cada classe tenha membros de sobra para o cv=10
        x, y = make_classification(n_samples=120, n_features=20, random_state=42)
        clf = GaussianNB()

        accuracy, precision, recall, f1 = self.service.decide_training(clf, x, y)

        self.assertIsInstance(accuracy, float)
        self.assertIsInstance(precision, float)
        self.assertIsInstance(recall, float)
        self.assertIsInstance(f1, float)
        self.assertTrue(0.0 <= accuracy <= 1.0)


if __name__ == '__main__':
    unittest.main()