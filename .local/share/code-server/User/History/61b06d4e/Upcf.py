from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
import motor.motor_asyncio
from typing import List, Dict
import json
import includes.Schemas as schemas
from includes.database.UserDB import UserDB
from includes.database.CantineMenuDB import CantineMenuDB
# Create the FastAPI instance
app = FastAPI()


# Load configuration from config.json
with open("config.json") as config_file:
    config = json.load(config_file)
# MongoDB settings
MONGODB_URL = f"mongodb://{config['mongodb']['db_username']}:{config['mongodb']['db_password']}@{config['mongodb']['db_hostname']}:{config['mongodb']['db_port']}/{config['mongodb']['db_name']}"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client["admin"]
auth_collection = db["auth"]

# Security settings
SECRET_KEY = config["secret_key"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await auth_collection.find_one({"email": username}, {"_id": 0})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await auth_collection.find_one({"email": username}, {"_id": 0})
    print("username:", user)
    if user is None:
        raise credentials_exception
    return {"email": user["email"]}


# Load configuration from config.json
with open("config.json") as config_file:
    config = json.load(config_file)


@app.on_event("startup")
async def startup_event():
    app.state.mongodb = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{config['mongodb']['db_username']}:{config['mongodb']['db_password']}@{config['mongodb']['db_hostname']}:{config['mongodb']['db_port']}/{config['mongodb']['db_name']}"
    )


@app.on_event("shutdown")
async def shutdown_event():
    app.state.mongodb.close()


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register_user(user: schemas.RegisterRequest):
    db_user = await auth_collection.find_one({"email": user.email}, {"_id": 0})
    print(user)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = {"email": user.email, "password": hashed_password, "devices": []}
    result = await auth_collection.insert_one(new_user)
    user_db = UserDB(app.state.mongodb)
    await user_db.initialize(user.email)
    return {"valid": True}

@app.get("/verify")
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    email = current_user["email"]
    return {"email": email}

@app.get("/profile")
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    email = current_user["email"]

    user_db = UserDB(app.state.mongodb)
    user_data = await user_db.get(email=email)
    return {"user_data": user_data}

@app.get("/cantine_menu")
async def today_food_menu(current_user: schemas.User = Depends(get_current_user)):
    cantine_menu_db = CantineMenuDB(app.state.mongodb)
    menu = await cantine_menu_db.get_all()
    return {"menu":menu}

@app.get("/today-food-menu")
async def today_food_menu(current_user: schemas.User = Depends(get_current_user)):
    pass

@app.get("/vote_hostel_meal")
async def vote_hostel_meal(meal_type:str,will_eat:str,current_user: schemas.User = Depends(get_current_user)):
    email = current_user['email']
    