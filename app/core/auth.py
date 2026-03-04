from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.dependencies import pegar_sessao
from app.models.models import Usuario
from app.core.security import bcrypt_context
from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# =========================================================
# 🔐 Configuração OAuth2
# =========================================================

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix="/auth", tags=["auth"])


# =========================================================
# 🔎 Função para autenticar usuário (email + senha)
# =========================================================

def autenticar_usuario(email: str, senha: str, session: Session):

    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    if not bcrypt_context.verify(senha, usuario.senha):
        return None

    return usuario


# =========================================================
# 🔑 Função para criar token JWT
# =========================================================

def criar_token(id_usuario: int):

    data_expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(id_usuario),
        "exp": data_expiracao
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


# =========================================================
# 🛡 Função para validar token e retornar usuário
# =========================================================

def verificar_token(
    token: str = Depends(oauth2_schema),
    session: Session = Depends(pegar_sessao)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return usuario


# =========================================================
# 🔑 Função para criar token JWT
# =========================================================

def criar_token(id_usuario: int):

    data_expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(id_usuario),
        "exp": data_expiracao
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


# =========================================================
# 🛡 Função para validar token e retornar usuário
# =========================================================

def verificar_token(
    token: str = Depends(oauth2_schema),
    session: Session = Depends(pegar_sessao)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return usuario