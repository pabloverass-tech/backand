from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.models import Usuario
from app.core.dependencies import autenticar_usuario, criar_token, pegar_sessao
from app.main import bcrypt_context
from app.schemas.schemas import UsuarioSchema


# Router responsável pelas rotas de autenticação
auth_router = APIRouter(prefix="/auth", tags=["auth"])


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


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    """
    Cria uma nova conta de usuário.

    - Verifica se o e-mail já existe
    - Criptografa a senha
    - Salva no banco
    """

    # 🔎 Verifica se já existe usuário com o mesmo e-mail
    usuario = (
        session.query(Usuario)
        .filter(Usuario.email == usuario_schema.email)
        .first()
    )

    if usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail do usuário já cadastrado"
        )

    # 🔐 Criptografa a senha antes de salvar
    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

    # ✅ Cria novo usuário usando parâmetros nomeados (boa prática)
    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=senha_criptografada,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin
    )

    # 💾 Salva no banco
    session.add(novo_usuario)
    session.commit()

    # 🔄 Atualiza objeto com ID gerado pelo banco
    session.refresh(novo_usuario)

    return {
        "mensagem": f"Usuário cadastrado com sucesso {novo_usuario.email}",
        "id": novo_usuario.id
    }


@auth_router.post("/login")
async def login(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    """
    Rota de login utilizando OAuth2 (form-data).

    ⚠ O campo 'username' do OAuth2PasswordRequestForm
    está sendo utilizado como e-mail.
    """

    # 🔎 Tenta autenticar usuário (email + senha)
    usuario = autenticar_usuario(
        email=dados_formulario.username,
        senha=dados_formulario.password,
        session=session
    )

    # ❌ Credenciais inválidas
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 🚫 Impede login de usuário inativo
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # 🔐 Gera token JWT (subject = id do usuário)
    access_token = criar_token(subject=str(usuario.id))

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }