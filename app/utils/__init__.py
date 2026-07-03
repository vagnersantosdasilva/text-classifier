import csv
import io
from typing import Tuple

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

def file_validation(file_path,separator):
    try:
        file = open(file_path,'r')
        reader = csv.reader(file,delimiter=separator)
        number_collums = len(next(reader))
        file.seek(0)
        for row in reader:
            # print(row)
            if len(row) != number_collums :
                file.close()
                return False
        file.close()
        return True
    except Exception:
        return False



