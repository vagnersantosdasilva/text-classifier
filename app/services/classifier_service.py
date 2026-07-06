import pickle

from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer

import utils
import pandas as pd
from app.repository import TrainingRepository
from app.models import Classe, TrainingStatus
from app.exceptions import TreinamentoError, ResourceNotFoundError


class ClassifierService:
    def __init__(self):
        self.training_repository = TrainingRepository()

    def classify_message(self, class_: Classe) -> Classe:
        try:
            training = self.training_repository.find_by_id(class_.id_training)
            if not training:
                raise ResourceNotFoundError(f"Treinamento {class_.id_training} não encontrado.")

            if training.status != TrainingStatus.COMPLETED:
                raise TreinamentoError(f"O treinamento não está pronto. Status: {training.status}")

            if not training.trained_model or not training.vectorizer:
                raise TreinamentoError("Modelo ou Vetorizador ausentes no banco de dados para este treinamento.")

            # RECONSTRÓI O MODELO E O VETORIZADOR CORRETOS
            predictor = pickle.loads(training.trained_model)
            vectorizer = pickle.loads(training.vectorizer)  # Nome batendo com o modelo do banco

            # Executa a classificação e atualiza o objeto original
            predicted_priority = self.classify(class_.message, predictor, vectorizer)
            class_.classe = predicted_priority

            return class_

        except Exception as e:
            print(f"Erro ao classificar mensagem: {e}")
            import traceback
            traceback.print_exc()
            raise TreinamentoError(f"Falha na classificação: {str(e)}")

    def classify(self, message: str, predictor, vectorizer) -> str:
        if not message or not message.strip():
            return "INDETERMINADA"  # Evita quebrar com strings vazias

        # Prepara o dado no formato que o pipeline de stop words espera
        df = pd.DataFrame(data={'description': [message]})
        docs_news, error = utils.remove_stop_words(df)

        # Garante o fallback caso a remoção de stop words falhe
        processed_text = docs_news.processed if docs_news is not None else [message]

        new_text_vector = vectorizer.transform(processed_text)

        classe_array = predictor.predict(new_text_vector)

        return str(classe_array[0])
