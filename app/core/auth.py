from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.dependencies import pegar_sessao
from app.models.usuario import Usuario
from app.core.security import bcrypt_context
from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# =========================================================
# 🔐 Configuração OAuth2
# =========================================================

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =========================================================
# 🔎 Função para autenticar usuário
# =========================================================

def autenticar_usuario(email: str, senha: str, session: Session):

    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    if not bcrypt_context.verify(senha, usuario.senha_hash):
        return None

    return usuario


# =========================================================
# 🔑 Criar token JWT
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
# 🔑 Criar Refresh token JWT
# =========================================================

def criar_refresh_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }

    return jwt.encode(payload, ALGORITHM, algorithm=ALGORITHM)

# =========================================================
# 🛡 Verificar token
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
        )

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return usuario
