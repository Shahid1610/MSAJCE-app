from pydantic import BaseModel
from typing import List, Optional




class User(BaseModel):
    email:str

class FoodItem(BaseModel):
    name: str
    description: str
    price: float

class DailyMenu(BaseModel):
    breakfast: List[FoodItem]
    lunch: List[FoodItem]
    dinner: List[FoodItem]


class Token(BaseModel):
    access_token: str
    token_type: str

class RegisterRequest(BaseModel):
    email:str
    password: str