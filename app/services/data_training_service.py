from concurrent.futures import ThreadPoolExecutor
from typing import List

from flask import current_app
from sqlalchemy.dialects.mysql import BIGINT

from app.exceptions import ResourceNotFoundError, AppException, TreinamentoError
from app.models import TrainingStatus, Training, Dataset
from app.models.training_model import VectorizerType
from app.repository.training_repository import TrainingRepository
from app.repository.dataset_repository import DatasetRepository

from sklearn.model_selection import cross_validate, LeaveOneOut
from sklearn.naive_bayes import MultinomialNB
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from app.ml import ClassicTfidfStrategy

import nltk
import utils
import pandas as pd
import io
import numpy as np

nltk.download('rslp')

from app.ml import VECTORIZATION_STRATEGY_MAP

class DataTrainingService:
    # Inicializamos o executor de forma estática ou dinâmica por demanda
    _executor = None
    def __init__(self):
        self.repository = TrainingRepository()
        self.dataset_repository = DatasetRepository()

    @classmethod
    def get_executor(cls):
        if cls._executor is None:
            # O Flask disponibiliza o config global aqui!
            max_workers = current_app.config.get('TRAINING_MAX_WORKERS', 2)
            cls._executor = ThreadPoolExecutor(max_workers=max_workers)
        return cls._executor


    def decide_training(self, clf, x, y):
        lines = x.shape[0];
        scoring = ['precision_macro', 'recall_macro', 'f1_macro', 'accuracy']
        cv = LeaveOneOut()
        # loo = LeaveOneOut()
        # for train, test in loo.split(x):
        # print("%s %s" % (train, test))
        # cv = KFold(n_splits=lines , shuffle=True ,random_state=45)

        if lines < 1000:

            scores = cross_validate(clf, x, y, cv=10, scoring=scoring)
            precision = np.mean([round(r, 4) for r in scores['test_precision_macro']])
            recall = np.mean([round(r, 4) for r in scores['test_recall_macro']])
            accuracy = np.mean([round(r, 4) for r in scores['test_accuracy']])
            f1 = np.mean([round(r, 4) for r in scores['test_f1_macro']])

            return accuracy, precision, recall, f1
        else:
            scores = cross_validate(clf, x, y, cv=5, scoring=scoring)
            precision = np.mean([ round(r, 4) for r in scores['test_precision_macro']])
            recall = np.mean([round(r, 4) for r in scores['test_recall_macro']])
            accuracy = np.mean([ round(r, 4) for r in scores['test_accuracy']])
            f1 = np.mean([round(r, 4) for r in scores['test_f1_macro']])
            return accuracy, precision, recall, f1


    def create_training(self,
                        dataset_id: BIGINT,
                        vectorizer_type = VectorizerType.TF_IDF,
                        use_stemmer = False) -> Training:

        # Não pode haver mais de 1 treinamento concorrente com o mesmo dataset
        dataset = self.dataset_repository.find_by_id(dataset_id)

        if dataset:
            count_training = self.repository.count_active_by_dataset(dataset_id)

            max_training_active_per_dataset = current_app.config.get('MAX_ACTIVE_TRAININGS_PER_DATASET')
            if count_training >= max_training_active_per_dataset:
                raise TreinamentoError(f"Limite de {max_training_active_per_dataset} treinamento(s) ativo(s) para este dataset atingido.")

            training_create = Training()
            training_create.id_dataset = dataset_id

            # Pedente aguardando inicio de treinamento e definindo tipos de vetorização
            training_create.status = TrainingStatus.PENDING
            training_create.vectorizer_type = vectorizer_type
            training_create.use_stemmer = use_stemmer

            training_response = self.repository.save(training_create)

            # Captura a instância real do app Flask para passar para a thread
            flask_app = current_app._get_current_object()

            # PASSAMOS o método, o app, o ID do treinamento e o ID do dataset
            #Inicia pool de threads para executar treinamentos concorrentes
            executor = self.get_executor()
            executor.submit(
                self.start_training,
                flask_app,
                training_response.id,
                dataset_id
            )
            return training_response
        else:
            raise ResourceNotFoundError("Dataset não encontrado para treinamento!")


    def start_training(self, app, training_id: BIGINT, dataset_id: BIGINT):
        # Cria o contexto do Flask dentro desta thread isolada para ver operações corretas de banco
        with app.app_context():
            training_status = None
            try:
                # Busca as instâncias dentro da nova sessão da thread
                training_status = self.repository.find_by_id(training_id)
                dataset = self.dataset_repository.find_by_id(dataset_id)

                if dataset is None or training_status is None:
                    raise ResourceNotFoundError("Dataset ou Treinamento não encontrado")

                training_status.id_dataset = dataset.id
                training_status.status = TrainingStatus.PROCESSING
                self.repository.save(training_status)

                # Resolve qual estratégia usar baseado na string do banco (ex: "TF_IDF")
                # Se vier vazio, assume a ClassicTfidfStrategy padrão
                strategy_class = VECTORIZATION_STRATEGY_MAP.get(
                    training_status.vectorizer_type, ClassicTfidfStrategy)

                # Instancia a estratégia injetando dinamicamente se quer usar stemmer ou não
                # A injeção de dependência resolve tudo aqui
                strategy_instance = strategy_class(
                    language=training_status.language,  # ex: 'english' ou 'portuguese'
                    use_stemmer=training_status.use_stemmer
                )

                data_frame, error_format = self.format_dataframe(dataset)

                if error_format:
                    raise TreinamentoError(f"Erro no dataframe: {error_format}")

                # 2 -  A 'estratégia' cuida de tudo!
                # Passamos direto os dados brutos extraídos de format_dataframe
                # TODO: description e priority ainda amarram o modelo . É preciso estudar uma forma de ser independente desse formato

                x = strategy_instance.fit_transform(data_frame['description'].tolist())
                y = data_frame['priority'].tolist()

                vc1 = VotingClassifier(
                    estimators=[
                        ('tree_clf', tree.DecisionTreeClassifier()),
                        ('gnb_clf', MultinomialNB()),
                        ('rnd_clf', RandomForestClassifier()),
                        ('svm_clf', SVC()),
                        ('knn_clf', KNeighborsClassifier(n_neighbors=3))
                    ], voting='hard'
                )

                accuracy, precision, recall, f1 = self.decide_training(vc1, x, y)
                predictor = vc1.fit(x, y)

                training_status.f1_score = float(f1)
                training_status.accuracy_score = float(accuracy)
                training_status.precision = float(precision)
                training_status.recall = float(recall)

                # Serializa o objeto do modelo (predictor) em bytes e o vetorizador
                import pickle
                training_status.trained_model = pickle.dumps(predictor)
                training_status.vectorizer = pickle.dumps(strategy_instance)  # Nome correto da coluna
                training_status.status = TrainingStatus.COMPLETED

                self.repository.save(training_status)

                print(f"----> TREINAMENTO {training_id} CONCLUÍDO COM SUCESSO!")

            except Exception as e:
                print(f"\n[ERRO CRÍTICO NO TREINAMENTO {training_id}]: {str(e)}")
                import traceback
                traceback.print_exc()
                from app.extensions import db
                try:
                    db.session.rollback()
                except:
                    pass

                if training_status:
                    try:
                        training_status.status = TrainingStatus.FAILED
                        self.repository.save(training_status)
                    except Exception as db_err:
                        print(f"Erro ao salvar status FAILED: {db_err}")


    def get_status_training(self, training_id: int) -> TrainingStatus:
        training_response = self.repository.find_by_id(training_id)
        if training_response:
            return training_response.status
        raise ResourceNotFoundError("O treinamento não foi encontrado!")


    def get_training_by_dataset(self, dataset_id: int) -> List[Training]:
        if self.dataset_repository.find_by_id(dataset_id) is None:
            raise ResourceNotFoundError('Dataset pesquisado não foi encontrado')
        return self.repository.find_by_dataset_id(dataset_id)


    def get_training_by_id(self, training_id: int) -> Training:
        training = self.repository.find_by_id(training_id)
        if training is None:
            raise ResourceNotFoundError('Treinamento pesquisado não foi encontrado')
        return training


    def get_all_trainings(self) -> List[Training]:
        return self.repository.find_all()


    def save_training(self, training: Training) -> Training:
        return self.repository.save_training(training)


    def format_dataframe(self, dataset: Dataset):
        try:
            if dataset:
                # 1. CORREÇÃO: Transforma os bytes do banco em um fluxo de arquivo lido nativamente pelo Pandas
                file_stream = io.BytesIO(dataset.file_content)

                # 2. Lê o CSV respeitando o caractere separador salvo no banco (limit_col ou separator)
                # Obs: Ajuste abaixo para dataset.limit_col se o atributo no modelo for limit_col
                separator = getattr(dataset, 'separator', getattr(dataset, 'limit_col', ';'))

                df = pd.read_csv(file_stream, sep=separator)

                # 3. Garante que as colunas necessárias existam
                if 'description' not in df.columns or 'priority' not in df.columns:
                    return AppException('CSV não possui as colunas description e priority.', 500), None

                # 4. Aplica sua função utilitária de tratamento UTF-8 na coluna de descrição
                df['description'] = utils.replace_utf8(df['description'].astype(str).tolist())

                # Retorna o DataFrame limpo e None para o erro
                return df, None

        except AttributeError:
            return AppException(
                'Erro ao tentar montar dataframe com dados de dataset. Verifique se o separador csv está correto',
                500), None
        except IndexError:
            return AppException(' Provável problema em separador', 500), None
        except Exception as error:
            # CORREÇÃO: Convertendo o erro explicitamente para string para evitar o TypeError
            return AppException('format_data_frame: ' + str(error), 500), None
