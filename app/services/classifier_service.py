import pickle
import unittest

from app.repository import TrainingRepository
from app.models import Classe, TrainingStatus
from app.exceptions import TreinamentoError, ResourceNotFoundError

class ClassifierService:
    def __init__(self):
        self.training_repository = TrainingRepository()

    def classify_message(self, class_: Classe) -> Classe:
        try:
            # 1. Validações iniciais de segurança
            if not class_.message or not class_.message.strip():
                class_.classe = "INDETERMINADA"
                return class_

            training = self.training_repository.find_by_id(class_.id_training)
            if not training:
                raise ResourceNotFoundError(f"Treinamento {class_.id_training} não encontrado.")

            if training.status != TrainingStatus.COMPLETED:
                raise TreinamentoError(f"O treinamento não está pronto. Status: {training.status}")

            if not training.trained_model or not training.vectorizer:
                raise TreinamentoError("Modelo ou Vetorizador ausentes no banco de dados para este treinamento.")

            # 2. RECONSTRÓI O PIPELINE (Desserialização)
            # VotingClassifier do scikit-learn
            # strategy  - Classe customizada (ClassicTfidfStrategy, BagOfWordsStrategy, etc.)
            predictor = pickle.loads(training.trained_model)
            strategy = pickle.loads(training.vectorizer)

            # 3. POLIMORFISMO EM AÇÃO
            # A própria estratégia já sabe o idioma, se usa stemmer e como limpar o texto.
            # Passamos a mensagem dentro de uma lista porque o scikit-learn espera um iterável.
            new_text_vector = strategy.transform([class_.message])

            # 4. PREDIÇÃO
            # O predict retorna um array numpy (ex: ['1']). Pegamos a primeira posição [0]
            classe_array = predictor.predict(new_text_vector)
            class_.classe = str(classe_array[0])

            return class_

        except Exception as e:
            print(f"Erro ao classificar mensagem: {e}")
            import traceback
            traceback.print_exc()
            raise TreinamentoError(f"Falha na classificação: {str(e)}")

