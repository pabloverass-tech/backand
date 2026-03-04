
from typing import Optional

from pydantic import BaseModel

class RegisterSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]
    
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str
    
    class Config:
        from_attributes = True

class RefreshSchema(BaseModel):
    refresh_token: str
    
    class Config:
        from_attributes = True
