from .vectorizer_strategy import ClassicTfidfStrategy
from .vectorizer_strategy import BagOfWordsStrategy
from .vectorizer_strategy import Word2VecStrategy

# Mapeamento de chaves string para as classes de estratégia correspondentes
VECTORIZATION_STRATEGY_MAP = {
    "TF_IDF": ClassicTfidfStrategy,
    "BAG_OF_WORDS": BagOfWordsStrategy,
    "WORD2VEC": Word2VecStrategy
}