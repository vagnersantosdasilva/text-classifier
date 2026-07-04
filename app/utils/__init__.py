import csv
import io
from typing import Tuple, List
import unidecode
import nltk
import string

def validate_csv_content(file_bytes: bytes, separator: str) -> Tuple[bool, str]:
    """
    Valida se o conteúdo do CSV está consistente.

    Args:
        file_bytes: Conteúdo do arquivo em bytes.
        separator: Caractere separador (ex: ',', ';').

    Returns:
        Tuple[bool, str]:
            - (True, "") se o CSV for válido.
            - (False, mensagem_de_erro) se houver problemas.
    """
    # 1. Tenta decodificar para string (assumindo UTF-8)
    try:
        content = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Se falhar, tenta com 'latin-1' como fallback ou levanta erro
        try:
            content = file_bytes.decode('latin-1')
        except UnicodeDecodeError:
            return False, "Arquivo não pôde ser decodificado como UTF-8 ou Latin-1. Verifique o encoding."

    # 2. Cria um objeto StringIO para simular um arquivo de texto
    csv_file = io.StringIO(content)

    # 3. Configura o leitor CSV
    try:
        reader = csv.reader(csv_file, delimiter=separator)
    except Exception as e:
        return False, f"Erro ao ler CSV com separador '{separator}': {str(e)}"

    # 4. Lê o cabeçalho (primeira linha)
    try:
        header = next(reader)
    except StopIteration:
        return False, "O arquivo está vazio (sem linhas)."

    if not header:
        return False, "A primeira linha (cabeçalho) está vazia."

    num_columns = len(header)

    # 5. Valida as linhas de dados
    for row_num, row in enumerate(reader, start=2):
        if len(row) != num_columns:
            return False, (
                f"Linha {row_num} tem {len(row)} colunas, "
                f"mas o cabeçalho tem {num_columns} colunas."
            )

    # 6. (Opcional) Verifica se todas as colunas têm nomes não vazios
    if any(not col.strip() for col in header):
        return False, "O cabeçalho contém colunas com nomes vazios (apenas espaços)."

    return True, ""


def file_validation(file_path, separator):
    try:
        file = open(file_path, 'r')
        reader = csv.reader(file, delimiter=separator)
        number_collums = len(next(reader))
        file.seek(0)
        for row in reader:
            # print(row)
            if len(row) != number_collums:
                file.close()
                return False
        file.close()
        return True
    except Exception:
        return False


def replace_utf8(list_str: List[str]) -> List[str]:
    result = []
    for phrase in list_str:
        result.append(phrase.replace("\\xc3\\xa7", "ç").replace("\\xc3\\xba", "ú").replace("\\xc3\\xa1", "á").replace(
            "\\xc3\\xaa",
            "ê").replace(
            "\\xc3\\xa3", "ã").replace("\\xc3\\xa9", "é").replace("\\xc3\\xb5", "õ").replace("\\xc3\\xad",
                                                                                             "í").replace(
            "\\xc3\\xa0", "à").replace("\\xc3\\xb3", "ó").replace("\\xc3\\x83", "Ã").replace("\\xc3\\xb4", "ô"))
    return result


def filter_unidecode(lista_de_frases):
    palavras_sem_acentos = [unidecode.unidecode(texto) for (texto) in lista_de_frases]
    return palavras_sem_acentos

def remove_stop_words(texts, language='portuguese'):
    stemmer = nltk.RSLPStemmer()
    exclude = set(string.punctuation)
    descriptions = texts.description
    descriptions_unidecode_filtered = filter_unidecode(descriptions)
    token_white_space = nltk.tokenize.WhitespaceTokenizer()
    stop_words = nltk.corpus.stopwords.words(language)
    stop_words_unidecode_filtered = filter_unidecode(stop_words)
    processed_sentence = list()
    for sentence in descriptions_unidecode_filtered:
        new_sentence = list()
        sentence_words = token_white_space.tokenize(sentence)
        for word in sentence_words:
            word = word.lower()
            if word not in stop_words_unidecode_filtered:
                word_ = ''.join(ch for ch in word if ch not in exclude)
                #if len(word_) >0 : word_ = stemmer.stem(word_)
                if len(word_) > 0: word_ = word_
                new_sentence.append(word_)
        processed_sentence.append(' '.join(new_sentence))

    texts['processed'] = processed_sentence
    #print(texts['processed'])
    return texts, None

