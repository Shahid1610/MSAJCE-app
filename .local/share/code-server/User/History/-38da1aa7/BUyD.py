from pydantic import BaseModel
from typing import List, Optional




class User(BaseModel):
    email:str

class CantineMenuItem(BaseModel):
    name: str
    meals:str
    description: str
    price: float

class HostelMenuItem(BaseModel):
    day: str
    meals:str
    name: str
    description: str



class Token(BaseModel):
    access_token: str
    token_type: str

class RegisterRequest(BaseModel):
    email:str
    password: str