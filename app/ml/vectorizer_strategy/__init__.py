# app/ml/strategies.py
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
#from nltk.stem import RSLPStemmer

nltk.download('stopwords', quiet=True)
nltk.download('rslp', quiet=True)  # Apenas para o caso de manter o RSLP


class BaseTextStrategy:
    def __init__(self, language='portuguese', use_stemmer=False):
        self.language = language
        self.use_stemmer = use_stemmer

        # Carrega as stop words do idioma escolhido de forma preventiva
        raw_stopwords = nltk.corpus.stopwords.words(language)
        # Se você tiver a sua utilidade 'filter_unidecode', aplique aqui:
        # self.stop_words = set(utils.filter_unidecode(raw_stopwords))
        self.stop_words = set(raw_stopwords)

        # Configura o Stemmer correto baseado no idioma
        if use_stemmer:
            if language == 'portuguese':
                # RSLP ainda é o melhor e mais agressivo para o nosso idioma
                self.stemmer = nltk.RSLPStemmer()
            else:
                # Snowball suporta 'english', 'spanish', 'french', etc.
                self.stemmer = nltk.snowball.SnowballStemmer(language)
        else:
            self.stemmer = None

    def _preprocess_text(self, text_list):
        """
        Substitui completamente o fluxo da sua antiga função 'remove_stop_words'.
        Processa a lista de textos aplicando Stop Words e Stemmer baseados no idioma da instância.
        """
        exclude = set(string.punctuation)
        token_white_space = nltk.tokenize.WhitespaceTokenizer()
        processed_sentences = []

        for sentence in text_list:
            new_sentence = []
            # Tokeniza por espaços em branco
            words = token_white_space.tokenize(str(sentence).lower())

            for word in words:
                # 1. Filtro de Stop Words
                if word not in self.stop_words:
                    # Remove pontuação
                    cleaned_word = ''.join(ch for ch in word if ch not in exclude)

                    if len(cleaned_word) > 0:
                        # 2. Aplica o Stemmer correto do idioma de forma dinâmica
                        if self.stemmer:
                            cleaned_word = self.stemmer.stem(cleaned_word)

                        new_sentence.append(cleaned_word)

            processed_sentences.append(' '.join(new_sentence))

        return processed_sentences


class ClassicTfidfStrategy(BaseTextStrategy):
    def __init__(self, language='portuguese', use_stemmer=False):
        super().__init__(language, use_stemmer)
        self.vectorizer = TfidfVectorizer()

    def fit_transform(self, text_list):
        # Executa a limpeza herdada do BaseTextStrategy
        cleaned_text = self._preprocess_text(text_list)
        return self.vectorizer.fit_transform(cleaned_text)

    def transform(self, text_list):
        cleaned_text = self._preprocess_text(text_list)
        return self.vectorizer.transform(cleaned_text)


class BagOfWordsStrategy(BaseTextStrategy):
    def __init__(self, language='portuguese', use_stemmer=False):
        super().__init__(language, use_stemmer)
        self.vectorizer = CountVectorizer()

    def fit_transform(self, text_list):
        cleaned_text = self._preprocess_text(text_list)
        return self.vectorizer.fit_transform(cleaned_text)

    def transform(self, text_list):
        cleaned_text = self._preprocess_text(text_list)
        return self.vectorizer.transform(cleaned_text)

# Exemplo de escalabilidade futura: Adicionar Word2Vec sem quebrar nada
class Word2VecStrategy(BaseTextStrategy):
    def __init__(self):
        # Aqui você inicializaria seu modelo genism/spacy futuramente
        pass
    def fit_transform(self, text_list):
        # Lógica para gerar os embeddings de treino
        pass
    def transform(self, text_list):
        # Lógica para gerar os embeddings de uma mensagem nova
        pass