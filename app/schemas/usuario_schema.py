
from typing import Optional

from pydantic import BaseModel

class RegisterSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

class LoginSchema(BaseModel):
    email: str
    senha: str

class RefreshSchema(BaseModel):
    refresh_token: str
