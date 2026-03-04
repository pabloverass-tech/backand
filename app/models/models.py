from sqlalchemy import (Column, DateTime, String, Integer, Float, Boolean, ForeignKey, Numeric, Enum)
from sqlalchemy.orm import relationship
# from sqlalchemy_utils.types import ChoiceType
import enum
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from datetime import datetime

# ======================
# CONEXÃO COM O BANCO   
# ======================

# Cria a conexão com o banco SQLite
# check_same_thread=False é necessário para FastAPI
db = create_engine("sqlite:///banco.db")
# db = create_engine("sqlite:///banco.db",connect_args={"check_same_thread": False})

# cria a base do banco de dados
Base = declarative_base()

# ======================
# ENUMS
# ======================

class StatusPedido(enum.Enum):
    PENDENTE = "PENDENTE"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"

# ======================
# MODELS
# ======================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    admin = Column(Boolean, default=False)
    
    def __init__(self, nome: str, email: str, senha: str, ativo: bool = True, admin: bool = False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin
    
    # Relacionamento: Um usuário tem muitos pedidos
    pedidos = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")
    

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)
    preco = Column(Float, default=0.0)
    
    # Relacionamento: Um pedido pertence a um usuário
    usuario = relationship("Usuario", back_populates="pedidos")
    # Relacionamento: Um pedido tem muitos itens    
    itens = relationship("ItemPedido", cascade="all,delete")

    def calcular_preco(self):
        # percorrer todos os itens do pedido
        # somar todos os precos de todos os itens dos pedidos
        # editar no campo "preco" o valor final do preco do pedido
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)
        

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)
    sabor = Column(String(50), nullable=False)
    tamanho = Column(String(20), nullable=False)
    preco_unitario = Column(Numeric(10, 2), default=0)

    # Relacionamento: Um item_pedido pertence a um pedido
    pedido = relationship("Pedido", back_populates="itens")