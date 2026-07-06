# app/controllers/__init__.py

# Importa o blueprint do arquivo que acabamos de criar
from .dataset_controller import dataset_bp

#Importa o bluepring do data_training_controller
from .data_training_controller import data_training_bp

#Importa o blueprint do classifier_controller
from .classifier_controller import classifier_bp

# Opcional: Se você tiver outros controllers no futuro, vai importá-los aqui também:
# from .user_controller import user_bp
# from .training_controller import training_bp