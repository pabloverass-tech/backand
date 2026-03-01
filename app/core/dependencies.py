from fastapi import Depends, HTTPException
from app.main import SECRET_KEY, ALGORITHM, oauth2_schema
from app.models.models import db
from app.models.models import Usuario
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from app.main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session   
    finally:
        session.close()
        
# Função auxiliar para validar as credenciais de login.
def autenticar_usuario(email, senha, session):
    # Realiza a busca no banco: Tenta encontrar o primeiro registro onde o e-mail bate
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    
    # Se a busca não retornar nada (usuário não encontrado), retorna False
    if not usuario:
        return False
    
    # Se o usuário existe, usamos o bcrypt para verificar se a senha digitada
    # é igual à senha criptografada salva no banco. Se não bater, retorna False.
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    
    # Se passou pelas duas validações acima (existe E senha bate), 
    # retorna o objeto completo do usuário (autenticação bem-sucedida).
    return usuario

#  Função responsável por gerar um token de acesso JWT (JSON Web Token).
def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    # Calcula a data e hora exata em que o token expirará.
    # Soma a duração definida (ex: 30 minutos) ao horário atual em UTC.
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    
    # Cria o 'payload' (o corpo do token), que é um dicionário com as informações essenciais:
    # "sub": Identifica o dono do token (Subject), aqui é o ID do usuário convertido para string.
    # "exp": Define o momento exato em que este token deixará de funcionar.
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    
     # Codifica o dicionário acima em uma string JWT.
    # Isso usa a chave secreta (SECRET_KEY) e o algoritmo (ALGORITHM) para assinar o token.
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    
     # Retorna o token gerado que será enviado para o front-end/usuário
    return jwt_codificado

# valida a assinatura e verifica se o dono do token ainda existe no banco de dados.
def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        # Tenta decodificar o token JWT usando a chave secreta e o algoritmo.
        # Se o token estiver expirado ou foi alterado (inválido), lança um erro JWTError.
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        
        # Extrai o ID do usuário do payload do token (campo 'sub' = Subject).
        # Converte para inteiro para garantir a integridade dos dados.
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        # Se a decodificação falhar, retorna 401 (Não Autorizado).
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    
    # Consulta o banco de dados para ver se o usuário desse ID ainda existe.
    # Mesmo o token sendo válido (assinatura ok), é bom garantir que a conta não foi deletada.
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    
    if not usuario:
        # Se o ID do token não encontrar nenhum usuário no DB, nega acesso.
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    
    # Se tudo estiver correto, retorna o objeto do usuário.
    # Nas rotas que usam essa função, a variável receberá esse objeto.
    return usuario
