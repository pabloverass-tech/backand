from fastapi import Depends, HTTPException
from app.models.models import Usuario
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from app.database.connection import SessionLocal
        
def pegar_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
