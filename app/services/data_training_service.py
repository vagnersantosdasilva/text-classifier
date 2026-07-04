from concurrent.futures import ThreadPoolExecutor

from mysql.ai.ml import classifier
from sqlalchemy.dialects.mysql import BIGINT

from app.exceptions import ResourceNotFoundError, AppException
from app.models import TrainingStatus, Training, Dataset
from app.repository.training_repository import TrainingRepository


import string
import threading

from pandas import DataFrame
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split, cross_validate, LeaveOneOut, KFold
from sklearn.naive_bayes import MultinomialNB
from sklearn import tree, metrics, model_selection
import nltk
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer, TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import unidecode
from werkzeug.utils import secure_filename
import repository
import utils
import pandas as pd
import io
from sklearn.model_selection import cross_val_score
import numpy as np

from repository.dataset_repository import DatasetRepository

nltk.download('rslp')



# Instancie o pool fora da classe (escopo global do módulo do service)
# para que todas as requisições usem a mesma fila
training_executor = ThreadPoolExecutor(max_workers=2)

class DataTrainingService:
    def __init__(self):
        self.repository = TrainingRepository()
        self.dataset_repository = DatasetRepository()

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
            precision = np.mean([100 * round(r, 4) for r in scores['test_precision_macro']])
            recall = np.mean([100 * round(r, 4) for r in scores['test_recall_macro']])
            accuracy = np.mean([100 * round(r, 4) for r in scores['test_accuracy']])
            f1 = np.mean([100 * round(r, 4) for r in scores['test_f1_macro']])
            # accuracy =  np.mean(cross_val_score(clf,x,y,cv=cv,  scoring="accuracy"))
            # precision = np.mean (cross_val_score(clf,x,y,cv=cv,  scoring='precision'))
            # recall = np.mean (cross_val_score(clf,x,y,cv=cv, scoring='recall'))
            # f1 = np.mean (cross_val_score(clf,x,y,cv=cv, scoring='f1'))
            return accuracy, precision, recall, f1
        else:
            scores = cross_validate(clf, x, y, cv=5, scoring=scoring)
            precision = np.mean([100 * round(r, 4) for r in scores['test_precision_macro']])
            recall = np.mean([100 * round(r, 4) for r in scores['test_recall_macro']])
            accuracy = np.mean([100 * round(r, 4) for r in scores['test_accuracy']])
            f1 = np.mean([100 * round(r, 4) for r in scores['test_f1_macro']])
            return accuracy, precision, recall, f1


    def create_training(self, dataset_id:BIGINT)->Training:
        #Não pode haver mais de 1 treinamento concorrente com o mesmo dataset


        dataset = self.dataset_repository.find_by_id(dataset_id)
        if dataset:
            training_create = Training()
            training_create.id_dataset = dataset_id

            #Pedente aguardando inicio de treinamento
            training_create.status = Training.Status.PENDING

            traing_response = repository.save(training_create)

            # Adiciona na fila do Pool. Se já tiver 2 rodando, essa aguarda.
            training_executor.submit(self.start_training,traing_response, dataset_id)

            return traing_response
        else:
            raise ResourceNotFoundError("Dataset não encontrado para treinamento!")

    def start_training(self, training_status: Training, dataset_id: BIGINT):
        '''TODO:
        - Pegar o id do dataset
        - Buscar o dataset no banco de dados
        - Obter o file_content do dataset
        - Fatiar o treinamento
        - Iniciar o treinamento
        - Retornar o status
        '''

        dataset = self.dataset_repository.find_by_id(dataset_id)

        if dataset:
            #print(dataset.file_content)
            data_frame, error_format = self.format_dataframe(dataset)

            #Retorna o dataframe com um novo campo 'processed'
            new_content, error_stop_words = utils.remove_stop_words(data_frame)

            tf_idf_X = TfidfVectorizer().fit_transform(new_content.processed)
            x = tf_idf_X
            y = new_content.priority

            gnb_clf = MultinomialNB()
            svm_clf = SVC()
            knn_clf = KNeighborsClassifier(n_neighbors=3)
            tree_clf = tree.DecisionTreeClassifier()
            rnd_clf = RandomForestClassifier()
            vc1 = VotingClassifier(
                estimators=([
                    ('tree_clf', tree_clf),
                    ('gnb_clf', gnb_clf),
                    ('rnd_clf', rnd_clf),
                    ('svm_clf', svm_clf),
                    ('knn_clf', knn_clf)]
                ), voting='hard'
            )

            accuracy, precision, recall, f1 = self.decide_training(vc1, x, y)

            training_status.id_dataset = dataset_id
            training_status.status = TrainingStatus.PROCESSING

            repository.update_training(training_status)

            predictor = vc1.fit(x, y)

            #training_status = Training()



            training_status.f1_score = float(f1)
            training_status.accuracy_score = float(accuracy)
            training_status.precision = float(precision)
            training_status.recall = float(recall)
            #training_status.cross_val_score_mean = float(cross_val_score)
            #Montando modelo de classificador
            classifier.predict = predictor
            classifier.data_frame = new_content

            #Salvando modelo e atualizando status
            training_status.trained_model = classifier
            training_status.status = Training.Status.COMPLETED

            repository.update_training(training_status)

        else:
            raise ResourceNotFoundError("Dataset não encontrado!")




    def stop_training(self):
        pass

    def get_status_training(self):
        pass

    def save_training(self, training :Training)->Training:
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


    #TODO: Regra de negócios -> Modelos de treinamento só poderão ser salvos com acurácia acima de 70%