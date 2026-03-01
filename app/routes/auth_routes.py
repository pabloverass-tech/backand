from fastapi import APIRouter, Depends, HTTPException
from app.models.models import Usuario
from app.core.dependencies import autenticar_usuario, criar_token, pegar_sessao, verificar_token
from app.main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from app.schemas.schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
   
    # Consulta o banco para verificar se já existe um usuário com este e-mail
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        # Se encontrar um usuário, lança uma exceção interrompendo o fluxo
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")
    else:
        # Segurança: Criptografa a senha antes de salvar no banco
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        
         # Instancia o novo objeto Usuario com os dados recebidos
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        
        # Salva e commita a transação no banco
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuário cadastrado com sucesso {usuario_schema.email}"}
    
# async def login(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
# usuario = autenticar_usuario(dados_formulario.email, dados_formulario.senha, session)
@auth_router.post("/login")
async def login(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    
    # Tenta autenticar o usuário.
    # Nota: O 'OAuth2PasswordRequestForm' espera o campo chamado 'username'.
    # Seu sistema usa e-mail, então 'dados_formulario.username' na verdade contém o e-mail.
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    
    # Se a autenticação falhar (usuário não existe ou senha errada), lança erro 400.
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    
    # Se a autenticação der certo, gera o Token de acesso usando o ID do usuário encontrado.
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    # verificar o token
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }