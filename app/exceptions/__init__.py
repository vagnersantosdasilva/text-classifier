# app/exceptions/__init__.py

class AppException(Exception):
    """
    Exceção base para toda a aplicação.
    Todas as outras exceções devem herdar desta.
    """
    def __init__(self, message, status_code=400, **kwargs):
        self.message = message
        self.status_code = status_code  # útil para retornar HTTP status adequado
        self.extra = kwargs
        super().__init__(message)

    def to_dict(self):
        """Converte a exceção para um dicionário (útil para respostas JSON)."""
        return {
            "erro": self.message,
            "status_code": self.status_code,
            "detalhes": self.extra
        }

#-----------Exceções recurso não encontrado ----------
class ResourceNotFoundError(AppException):
    def __init__(self, message="Recurso não foi encontrado", **kwargs):
        super().__init__(message, status_code=404, **kwargs)

# ---------- Exceções relacionadas a Dataset ----------
class DatasetError(AppException):
    """Exceção base para erros no domínio de dataset."""
    pass

class DatasetInvalidoError(DatasetError):
    """Lançada quando os dados do dataset são inválidos (ex: separador incorreto)."""
    def __init__(self, message="Dados do dataset inválidos", **kwargs):
        super().__init__(message, status_code=400, **kwargs)

class DatasetDuplicadoError(DatasetError):
    """Lançada quando já existe um dataset com o mesmo nome."""
    def __init__(self, nome, **kwargs):
        message = f"Dataset com nome '{nome}' já existe"
        super().__init__(message, status_code=409, nome=nome, **kwargs)

class DatasetNaoEncontradoError(DatasetError):
    """Lançada quando um dataset com o ID informado não existe."""
    def __init__(self, dataset_id=None, **kwargs):
        message = f"Dataset com ID '{dataset_id}' não encontrado" if dataset_id else "Dataset não encontrado"
        super().__init__(message, status_code=404, dataset_id=dataset_id, **kwargs)

class DatasetArquivoError(DatasetError):
    """Lançada quando há problemas com o arquivo do dataset (ex: leitura, tamanho)."""
    def __init__(self, message="Erro no arquivo do dataset", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


# ---------- Exceções relacionadas a Treinamento ----------
class TreinamentoError(AppException):
    """Exceção base para erros no treinamento."""
    def __init__(self, message="Erro no treinamento", status_code=400, **kwargs):
        super().__init__(message, status_code, **kwargs)

class TreinamentoInvalidoError(TreinamentoError):
    """Lançada quando os parâmetros de treinamento são inválidos."""
    def __init__(self, message="Parâmetros de treinamento inválidos", **kwargs):
        super().__init__(message, status_code=400, **kwargs)

class TreinamentoStatusError(TreinamentoError):
    """Lançada quando o status do treinamento não permite a ação solicitada."""
    def __init__(self, status_atual, acao, **kwargs):
        message = f"Não é possível '{acao}' pois o treinamento está com status '{status_atual}'"
        super().__init__(message, status_code=409, status=status_atual, **kwargs)


# ---------- Exceções relacionadas a Classificação ----------
class ClassificacaoError(AppException):
    """Exceção base para erros na classificação."""
    def __init__(self, message="Erro na classificação", status_code=400, **kwargs):
        super().__init__(message, status_code, **kwargs)

class ModeloNaoTreinadoError(ClassificacaoError):
    """Lançada quando o modelo ainda não foi treinado ou está indisponível."""
    def __init__(self, message="Modelo não treinado", **kwargs):
        super().__init__(message, status_code=400, **kwargs)