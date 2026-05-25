from functools import wraps
from flask import session, make_response, jsonify


def login_required(f):
    """
    Decorator que verifica se o usuário está logado.
    Se não estiver, retorna um erro 401 com mensagem de autenticação necessária.
    
    Uso:
    @login_required
    @app.route('/minha-rota/', methods=['GET'])
    def minha_rota():
        # seu código aqui
        pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se o usuário_id está armazenado na sessão
        if 'usuario_id' not in session:
            return make_response(
                jsonify(mensagem="Autenticação necessária. Faça login para acessar este recurso."),
                401
            )
        
        # Se estiver logado, executa a função normalmente
        return f(*args, **kwargs)
    
    return decorated_function
