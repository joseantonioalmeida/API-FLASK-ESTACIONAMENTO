import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, make_response, jsonify
from dotenv import load_dotenv


load_dotenv()


# Configurações JWT
SECRET_KEY = os.getenv('jwt_secret_key', 'change-me-to-a-secure-key')
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 24  # Token válido por 24 horas

# Blacklist de tokens inválidos (logout)
# Formato: {token_jti: data_expiracao}
token_blacklist = {}

def gerar_token_jwt(usuario_id: int, usuario_email: str, usuario_username: str) -> str:
    """
    Gera um token JWT com as informações do usuário.
    
    Args:
        usuario_id: ID do usuário
        usuario_email: Email do usuário
        usuario_username: Username do usuário
    
    Returns:
        Token JWT codificado como string
    
    Exemplo:
        token = gerar_token_jwt(1, 'user@email.com', 'username')
    """
    payload = {
        'usuario_id': usuario_id,
        'usuario_email': usuario_email,
        'usuario_username': usuario_username,
        'iat': datetime.utcnow(),  # Issued at
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)  # Expiration
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def validar_token_jwt(token: str) -> dict:
    """
    Valida um token JWT e retorna o payload decodificado.
    
    Args:
        token: Token JWT a ser validado
    
    Returns:
        Dicionário com os dados decodificados (usuario_id, usuario_email, usuario_username)
    
    Raises:
        jwt.ExpiredSignatureError: Se o token expirou
        jwt.InvalidTokenError: Se o token é inválido
    
    Exemplo:
        payload = validar_token_jwt('eyJhbGc...')
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token expirou.")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token inválido.")


def extrair_token_do_header(authorization_header: str) -> str:
    """
    Extrai o token JWT do header Authorization.
    
    Formato esperado: "Bearer <token>"
    
    Args:
        authorization_header: Valor do header Authorization
    
    Returns:
        Token JWT extraído
    
    Raises:
        ValueError: Se o formato do header é inválido
    
    Exemplo:
        token = extrair_token_do_header('Bearer eyJhbGc...')
    """
    if not authorization_header:
        raise ValueError("Header Authorization não fornecido.")
    
    partes = authorization_header.split()
    
    if len(partes) != 2 or partes[0].lower() != 'bearer':
        raise ValueError("Formato de Authorization inválido. Use: Bearer <token>")
    
    return partes[1]


def limpar_blacklist_expirada():
    """
    Remove tokens expirados da blacklist para economizar memória.
    """
    global token_blacklist
    tokens_expirados = [
        token for token, data_exp in token_blacklist.items() 
        if datetime.utcnow() > data_exp
    ]
    for token in tokens_expirados:
        token_blacklist.pop(token, None)


def adicionar_token_blacklist(token: str, data_expiracao: datetime):
    """
    Adiciona um token à blacklist (usado no logout).
    
    Args:
        token: Token JWT a ser inválido
        data_expiracao: Data de expiração do token
    """
    global token_blacklist
    limpar_blacklist_expirada()
    token_blacklist[token] = data_expiracao


def token_esta_na_blacklist(token: str) -> bool:
    """
    Verifica se um token está na blacklist.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        True se o token está na blacklist, False caso contrário
    """
    return token in token_blacklist


def token_requerido(f):
    """
    Decorator que verifica se um token JWT válido foi fornecido.
    
    O token deve ser enviado no header Authorization com o formato:
    Authorization: Bearer <token>
    
    Se o token for válido, o payload decodificado é adicionado ao request.jwt_payload
    
    Se não estiver válido ou não for fornecido, retorna erro 401.
    
    Uso:
        @token_requerido
        @app.route('/usuarios/', methods=['GET'])
        def listar_usuarios():
            usuario_id = request.jwt_payload['usuario_id']
            # seu código aqui
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extrai o header Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return make_response(
                jsonify(mensagem="Token JWT não fornecido. Adicione o header Authorization: Bearer <token>"),
                401
            )
        
        try:
            # Extrai o token do header
            token = extrair_token_do_header(auth_header)
            
            # Verifica se o token está na blacklist (foi feito logout)
            if token_esta_na_blacklist(token):
                return make_response(
                    jsonify(mensagem="Token inválido. Você foi desconectado (logout realizado). Faça login novamente."),
                    401
                )
            
            # Valida o token e obtém o payload
            payload = validar_token_jwt(token)
            
            # Adiciona o payload ao request para usar na função
            request.jwt_payload = payload  #type:ignore
            
        except ValueError as e:
            # Erro no formato do header
            return make_response(
                jsonify(mensagem=str(e)),
                401
            )
        except jwt.ExpiredSignatureError:
            return make_response(
                jsonify(mensagem="Token expirou. Faça login novamente."),
                401
            )
        except jwt.InvalidTokenError:
            return make_response(
                jsonify(mensagem="Token inválido. Faça login novamente."),
                401
            )
        
        # Se tudo estiver OK, executa a função
        return f(*args, **kwargs)
    
    return decorated_function
