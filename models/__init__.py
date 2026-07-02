class Dataset:
    def __init__(self, name=None, file_content=None, separator=None, id=None):
        self.id = id
        self.name = name
        self.file_content = file_content
        self.separator = separator


class Training:
    def __init__(self, id_dataset=None, status=None, id_training=None, f1_score=None, precision=None, recall=None,
                 accuracy_score=None , cross_val_score_mean=None):
        self.id = id_training
        self.status = status
        self.id_dataset = id_dataset
        self.f1_score = f1_score
        self.precision = precision
        self.recall = recall
        self.accuracy_score = accuracy_score
        self.cross_val_score_mean = cross_val_score_mean


class Error:
    def __init__(self, message, code):
        self.message = message
        self.code = code


class Classifier:
    def __init__(self, predict=None,  data_frame=None):
        self.predict = predict
        self.data_frame = data_frame
