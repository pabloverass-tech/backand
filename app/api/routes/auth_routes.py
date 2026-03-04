from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import autenticar_usuario, criar_token, verificar_token
from app.core.dependencies import pegar_sessao
from app.core.security import hash_password
from app.models.usuario import Usuario
from app.schemas.usuario_schema import LoginSchema, RegisterSchema


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
async def criar_conta(usuario_schema: RegisterSchema, session: Session = Depends(pegar_sessao)):

    # Verifica se já existe usuário com o mesmo e-mail
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

    # Criptografa a senha antes de salvar
    senha_criptografada = hash_password(usuario_schema.senha)

    # Cria a instância do usuário usando parâmetros nomeados
    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=senha_criptografada,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin
    )

    # Adiciona e confirma a transação no banco
    session.add(novo_usuario)
    session.commit()

    # Atualiza o objeto com os dados reais do banco (ex: ID gerado)
    session.refresh(novo_usuario)

    # Debug opcional
    print("Usuário criado:", novo_usuario.__dict__)

    # Retorna resposta ao cliente
    return {
        "mensagem": f"Usuário cadastrado com sucesso {novo_usuario.email}",
        "id": novo_usuario.id
    }
    

@auth_router.post("/login")
async def login(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    """
    Rota de login usando OAuth2 (form-data).

    O campo 'username' será usado como e-mail.
    """

    usuario = autenticar_usuario(
        email=dados_formulario.username,
        senha=dados_formulario.password,
        session=session
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    access_token = criar_token(usuario.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.get("/me")
async def usuario_logado(usuario: Usuario = Depends(verificar_token)):
    """
    Retorna os dados do usuário autenticado.
    Rota protegida por token.
    """

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "admin": usuario.admin
    }