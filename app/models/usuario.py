from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)