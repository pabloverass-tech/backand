from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic_settings import BaseSettings
# ==============================
# CONFIGURAÇÕES DE SEGURANÇA
# ==============================

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
# cria um objeto global com as configurações

# configuração do algoritmo de hash da senha
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ==============================
# TOKEN (JWT)
# ==============================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT com tempo de expiração.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ---------------------------------------------------
# FUNÇÃO PARA CRIPTOGRAFAR SENHA
# ---------------------------------------------------
def hash_senha(senha: str):
    """
    Recebe uma senha em texto
    e retorna ela criptografada
    """
    return pwd_context.hash(senha)


# ---------------------------------------------------
# FUNÇÃO PARA VERIFICAR SENHA
# ---------------------------------------------------
def verificar_senha(senha: str, hash: str):
    """
    Verifica se a senha digitada
    corresponde ao hash salvo no banco
    """
    return pwd_context.verify(senha, hash)