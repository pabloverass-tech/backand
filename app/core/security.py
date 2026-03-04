from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

# ==============================
# CONFIGURAÇÕES DE SEGURANÇA
# ==============================

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Contexto único para hash de senha
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


# ==============================
# HASH DE SENHA
# ==============================

def hash_password(password: str) -> str:
    """
    Gera o hash da senha usando bcrypt.
    """
    return pwd_context.hash(password[:72])  # Trunca senha para 72 bytes


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return pwd_context.verify(password, hashed)