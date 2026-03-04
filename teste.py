from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Usuario  # seu model real

# 🔹 URL do seu banco
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/autoescola"

# 🔹 cria engine
engine = create_engine(DATABASE_URL)

# 🔹 cria sessão
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 🔹 cria objeto
novo_usuario = Usuario(
    nome="pablo veras",
    email="pabloveras11s@gmail.com",
    senha="123",
    ativo=True,
    admin=True
)

# 🔹 adiciona no banco
session.add(novo_usuario)
session.commit()

# 🔹 mostra no terminal
print("Objeto criado:")
print(novo_usuario.__dict__)

session.close()