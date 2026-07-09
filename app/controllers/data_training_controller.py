from flask import Blueprint, jsonify, request
from app.services.data_training_service import DataTrainingService
from app.exceptions import ResourceNotFoundError

# Cria o Blueprint com prefixo /api/training
data_training_bp = Blueprint('data_training', __name__, url_prefix='/api')


@data_training_bp.route('/training/status/<int:training_id>', methods=['GET'])
def status(training_id):
    """
        Consulta apenas o status atual de execução de um treinamento
        ---
        tags:
          - Treinamento
        parameters:
          - name: training_id
            in: path
            type: integer
            required: true
            description: ID único do treinamento.
        responses:
          200:
            description: Status retornado com sucesso.
        """
    try:
        data_training_service = DataTrainingService()
        status = data_training_service.get_status_training(training_id)
        return jsonify({
            "id": training_id,
            "satus": status
        }), 200
    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@data_training_bp.route('/training', methods=['POST'])
def start_training():
    """
        Inicia um processo assíncrono de treinamento via Thread Pool
        ---
        tags:
          - Treinamento
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                id_dataset:
                  type: integer
                  description: ID do arquivo de dataset previamente persistido no banco.
                  example: 1
                vectorizer_type:
                  type: string
                  enum: [TF_IDF, BAG_OF_WORDS, WORD2VEC]
                  default: TF_IDF
                  description: Estratégia matemática de vetorização de texto a ser aplicada.
                use_stemmer:
                  type: boolean
                  default: false
                  description: Indica se aplicará redução de radicais (RSLPStemmer/Snowball) na preparação.
        responses:
          200:
            description: Registro de treinamento inserido como PENDING e enviado para a thread de processamento.
        """
    try:
        # Criação de um treinamento e retorno de status inicial ou mensagem de erro
        # 1. Captura o JSON enviado no body
        dados = request.get_json()

        # 2. Garante que o JSON não veio vazio e extrai o id_dataset
        if not dados or 'id_dataset' not in dados:
            return jsonify({"erro": "O campo 'id_dataset' é obrigatório no JSON"}), 400

        # Obtendo os dados
        dataset_id = dados.get('id_dataset')
        vectorizer_type = dados.get('vectorizer_type')
        use_stemmer = dados.get('use_stemmer')

        data_training_service = DataTrainingService()
        training = data_training_service.create_training(dataset_id, vectorizer_type, use_stemmer)
        return jsonify(training.to_dict()), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@data_training_bp.route('/training/<int:training_id>', methods=['GET'])
def get_training(training_id):
    """
        Recupera os detalhes completos (incluindo métricas estatísticas) de um treinamento específico
        ---
        tags:
          - Treinamento
        parameters:
          - name: training_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Detalhes carregados com sucesso.
        """
    try:
        training = DataTrainingService().get_training_by_id(training_id)
        return jsonify(training.to_dict()), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@data_training_bp.route('dataset/<int:dataset_id>/training', methods=['GET'])
def get_training_list(dataset_id):
    """
        Lista todos os históricos de treinamentos associados a um dataset específico
        ---
        tags:
          - Treinamento
        parameters:
          - name: dataset_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Lista de treinamentos retornada.
    """
    try:
        list_training = DataTrainingService().get_training_by_dataset(dataset_id)
        # Converte a lista de objetos do banco para uma lista de dicionários
        trainings_response = [training.to_dict() for training in list_training]

        return jsonify(trainings_response), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()  # Isso garante que você veja o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500


@data_training_bp.route('/training/<int:training_id>', methods=['DELETE'])
def delete_training(training_id):
    """
    Apaga fisicamente um treinamento do banco de dados
    ---
    tags:
      - Treinamento
    parameters:
      - name: training_id
        in: path
        type: integer
        required: true
        description: ID único do treinamento que deseja remover.
    responses:
      204:
        description: Treinamento deletado com sucesso. Não retorna corpo de resposta.
      404:
        description: O treinamento informado não foi encontrado.
      500:
        description: Erro interno no servidor.
    """
    try:
        DataTrainingService().remove_training(training_id)
        # 204 No Content por convenção REST não deve retornar corpo (JSON), apenas o status
        return '', 204

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500
