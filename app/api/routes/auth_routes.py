
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import pegar_sessao
from app.models.usuario import Usuario
from app.schemas.usuario_schema import RegisterSchema
from app.main import bcrypt_context

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: RegisterSchema, session: Session = Depends(pegar_sessao)):
   
    # Consulta o banco para verificar se já existe um usuário com este e-mail
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()

    if usuario:
        # Se encontrar um usuário, lança uma exceção interrompendo o fluxo
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")
    else:
        # Segurança: Criptografa a senha antes de salvar no banco
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        
        #  Instancia o novo objeto Usuario com os dados recebidos
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        
        # Salva e commita a transação no banco
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuário cadastrado com sucesso {usuario_schema.email}"}

