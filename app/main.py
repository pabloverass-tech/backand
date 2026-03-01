from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Cria a aplicação FastAPI
app = FastAPI(
    title="API Pedidos",
    version="1.0.0")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

# Importa as rotas de autenticação
from app.routes.auth_routes import auth_router
# Importa as rotas de pedidos (orders)
from app.routes.pedido_routes import pedidos_router

# Registra as rotas na aplicação principal
app.include_router(auth_router)
app.include_router(pedidos_router)

# para rodar o nosso código, executar no terminal: uvicorn main:app --reload
# uvicorn app.main:app --reload