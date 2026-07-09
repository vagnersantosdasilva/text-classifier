from email import message

from flask import Blueprint, jsonify, request
from app.services.classifier_service import ClassifierService
from app.exceptions import ResourceNotFoundError
from app.models import Classe

# Cria o Blueprint com prefixo /api/training
classifier_bp = Blueprint('classifier', __name__, url_prefix='/api/classifier')


@classifier_bp.route('/', methods=['POST'])
def classifier():
    """
        Classifica uma mensagem de texto usando um modelo treinado
        ---
        tags:
          - Classificação
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                id_training:
                  type: integer
                  description: ID do treinamento cujos pesos/pipeline salvos no banco serão usados para predizer.
                  example: 1
                message:
                  type: string
                  description: O corpo da mensagem/email de texto que precisa ser categorizado.
                  example: "Minha senha de acesso expirou e o banco de dados retornou erro 500"
        responses:
          200:
            description: Mensagem classificada com sucesso.
            schema:
              type: object
              properties:
                id_training:
                  type: integer
                message:
                  type: string
                classe:
                  type: string
                  description: A classe predita pelo VotingClassifier.
          400:
            description: Campos obrigatórios ausentes no JSON.
          404:
            description: O ID do treinamento informado não existe no banco de dados.
          500:
            description: Erro interno no processamento.
        """
    try:
        # 1. Captura o JSON enviado no body
        dados = request.get_json()

        id_training = dados.get('id_training')
        message = dados.get('message')

        # 2. Garante que o JSON não veio vazio e extrai o id_dataset
        if not id_training:
            return jsonify({"erro": "O campo 'id_training' é obrigatório no JSON"}), 400
        if not message:
            return jsonify({"erro": "O campo mensagem é obrigatório no JSON"}), 400

        classe_input = Classe(id_training=id_training, message=message)

        service = ClassifierService()
        classe_response = service.classify_message(classe_input)

        return jsonify({
            "id_training": classe_response.id_training,
            "message": classe_response.message,
            "classe": classe_response.classe[0]
        }), 200

    except ResourceNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        import traceback
        traceback.print_exc()  # Pra garantir que ver o erro real no terminal se algo falhar
        return jsonify({"erro": "Erro interno no servidor", "detalhe": str(e)}), 500
