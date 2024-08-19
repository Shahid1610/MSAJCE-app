from pydantic import BaseModel
from typing import List, Optional


class RegisterRequest(BaseModel):
    email:str
    password: str


class User(BaseModel):
    email:str


class Token(BaseModel):
    access_token: str
    token_type: str

class Address(BaseModel):
    street: str
    city: str
    state: str
    pincode: int

class Phone(BaseModel):
    phone: str

class PlaceOrderRequest(BaseModel):
    quantity:int
class CancelOrderRequest(BaseModel):
    oid:str