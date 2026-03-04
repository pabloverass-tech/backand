from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ======================
# CONEXÃO COM O BANCO   
# ======================

DATABASE_URL = "sqlite:///banco.db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()