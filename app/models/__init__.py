from .dataset_model import Dataset
from .training_model import Training, TrainingStatus

class Error:
    def __init__(self, message, code):
        self.message = message
        self.code = code


class Classifier:
    def __init__(self, predict=None, data_frame=None):
        self.predict = predict
        self.data_frame = data_frame

class Classe:
    def __init__(self,id_training=None, message=None, classe=None):
        self.id_training = id_training
        self.message = message
        self.classe = classe
    def to_dict(self):
        return {
            "classe": self.classe,
            "id_training": self.id_training,
            "message": self.message
        }