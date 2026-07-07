# tests/test_strategies.py
import unittest
import scipy.sparse
# Importação absoluta a partir da raiz do seu projeto
from app.ml.vectorizer_strategy import ClassicTfidfStrategy, BagOfWordsStrategy


class TestTextStrategies(unittest.TestCase):

    def test_tfidf_strategy_outputs_correct_shape(self):
        """Valida se a estratégia gera uma matriz esparsa com as dimensões corretas"""
        strategy = ClassicTfidfStrategy(language='portuguese', use_stemmer=False)

        textos_treino = [
            "o sistema apresentou um erro de banco",
            "solicito suporte para alteração de senha"
        ]

        # 1. Testa o treinamento (fit_transform)
        matriz_treino = strategy.fit_transform(textos_treino)

        # O Scikit-Learn deve retornar uma matriz esparsa do SciPy
        self.assertTrue(scipy.sparse.issparse(matriz_treino))
        # Deve ter 2 linhas (uma para cada texto)
        self.assertEqual(matriz_treino.shape[0], 2)

        # 2. Testa a classificação (transform) com um texto novo
        texto_novo = ["erro no banco"]
        matriz_nova = strategy.transform(texto_novo)

        self.assertEqual(matriz_nova.shape[0], 1)
        # O número de colunas do texto novo DEVE ser idêntico ao do treino
        self.assertEqual(matriz_nova.shape[1], matriz_treino.shape[1])

    def test_stop_words_filtering_by_language(self):
        """Valida se as stop words de idiomas diferentes estão sendo aplicadas"""
        # Se usarmos stop words de inglês, a palavra "o" e "de" do português NÃO devem sumir
        strategy_en = ClassicTfidfStrategy(language='english', use_stemmer=False)

        strategy_en.fit_transform(["o erro de conexão"])
        vocab_en = strategy_en.vectorizer.vocabulary_

        print(vocab_en)


        self.assertIn('de', vocab_en)

        # Agora testamos com a estratégia em português
        strategy_pt = ClassicTfidfStrategy(language='portuguese', use_stemmer=False)
        strategy_pt.fit_transform(["o erro de conexão"])
        vocab_pt = strategy_pt.vectorizer.vocabulary_

        self.assertNotIn('o', vocab_pt)
        self.assertNotIn('de', vocab_pt)

    def test_stemmer_extraction(self):
        """Valida se o stemmer está extraindo o radical das palavras corretamente"""
        strategy = ClassicTfidfStrategy(language='portuguese', use_stemmer=True)

        strategy.fit_transform(["eu vou treinar o modelo de treinamento"])
        vocab = strategy.vectorizer.vocabulary_
        print (vocab)

        # As palavras inteiras não devem existir isoladas no vocabulário, apenas seus radicais
        self.assertNotIn("treinamento", vocab)
        self.assertNotIn("treinar", vocab)
        self.assertIn("trein", vocab)


if __name__ == '__main__':
    unittest.main()

# Comando de execução
# python -m unittest discover -s tests