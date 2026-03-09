from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.database.connection import BaseModel
import enum


class PerfilEnum(enum.Enum):
    
    ADMIN = "admin"
    INSTRUTOR = "instrutor"
    ALUNO ="aluno"

class Usuario(BaseModel):
    """Esquema base para usuário"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    perfil = Column(Enum(PerfilEnum), default=PerfilEnum.INSTRUTOR)
