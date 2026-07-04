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
