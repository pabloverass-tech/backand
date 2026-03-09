from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.security import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

from app.core.auth import autenticar_usuario, criar_refresh_token, criar_token, verificar_token
from app.core.dependencies import pegar_sessao
from app.core.security import hash_senha
from app.models.usuario import Usuario
from app.schemas.usuario_schema import LoginSchema, RegisterSchema


# =========================================================
# CONFIGURAÇÃO DO ROUTER
# =========================================================

auth_router = APIRouter(prefix="/auth", tags=["auth"])


# =========================================================
# ROTA BASE DE AUTENTICAÇÃO
# =========================================================

@auth_router.get("/")
async def home():
    """
    Rota base de autenticação.
    Apenas retorna uma mensagem simples para teste.
    """
    return {
        "mensagem": "Você acessou a rota padrão de autenticação",
        "autenticado": False
    }


# =========================================================
# ENDPOINT CRIAR CONTA
# =========================================================

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: RegisterSchema, session: Session = Depends(pegar_sessao)):

    # Verifica se já existe usuário com o mesmo email
    usuario = (
        session.query(Usuario)
        .filter(Usuario.email == usuario_schema.email)
        .first()
    )

    if usuario:
        raise HTTPException(
            status_code=400,
            detail="E-mail do usuário já cadastrado"
        )

    # Criptografa a senha antes de salvar no banco
    senha_criptografada = hash_senha(usuario_schema.senha)

    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha_hash=senha_criptografada,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin
    )

    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    # DEBUG opcional
    print("Usuário criado:", novo_usuario.__dict__)

    return {
        "mensagem": f"Usuário cadastrado com sucesso {novo_usuario.email}",
        "id": novo_usuario.id
    }


# =========================================================
# ENDPOINT LOGIN
# =========================================================

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):

    # Verifica se o usuário existe e se a senha está correta
    usuario = autenticar_usuario(
        form_data.username,
        form_data.password,
        session=session
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se o usuário está ativo
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Cria token JWT
    access_token = criar_token(usuario.id)

     # cria refresh token
    refresh_token = criar_refresh_token(usuario.id)

    # Retorna token e dados do usuário
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "admin": usuario.admin
        }
    }


# =========================================================
# ENDPOINT POST / REFRESH
# =========================================================
@auth_router.post("/refresh")
async def refresh_token(refresh_token: str):
    # recebe refresh token enviado pelo frontend

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        # decodifica o token e valida assinatura

        if payload.get("type") != "refresh":
            # verifica se realmente é um refresh token

            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        # pega o id do usuário dentro do token
        user_id = payload.get("sub")

        # gera um novo access token
        new_access_token = criar_token(user_id)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        # retorna o novo token

    except JWTError:
        # erro caso o token seja inválido ou expirado

        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido"
        )


# =========================================================
# ENDPOINT USUÁRIO LOGADO
# =========================================================

@auth_router.get("/me")
async def usuario_logado(usuario: Usuario = Depends(verificar_token)):

    # Endpoint protegido.
    # Retorna os dados do usuário autenticado a partir do token JWT.
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "admin": usuario.admin
    }

# =========================================================
# DEPENDÊNCIA PARA ROTAS DE ADMIN
# =========================================================

def verificar_admin(usuario: Usuario = Depends(verificar_token)):
    """
    Dependência usada para proteger rotas administrativas.
    Apenas usuários com admin=True podem acessar.
    """

    if not usuario.admin:
        raise HTTPException(
            status_code=403,
            detail="Permissão insuficiente"
        )

    return usuario




# async def criar_pedido(descricao: str,session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):