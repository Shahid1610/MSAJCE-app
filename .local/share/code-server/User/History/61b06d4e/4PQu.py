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
from includes.database.HostelMenuDB import HostelMenuDB
from includes.database.TodayDataDB import TodayDataDB
from includes.database.HostelVotingDB import HostelVotingDB
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


@app.get("/vote_hostel_meal")
async def vote_hostel_meal(meal_type: str, will_eat: str, current_user: schemas.User = Depends(get_current_user)):
    if meal_type not in ['breakfast', 'lunch', 'dinner']:
        raise HTTPException(status_code=400, detail="Invalid meal type")

    if will_eat not in ['yes', 'no']:
        raise HTTPException(status_code=400, detail="Invalid value for will_eat")

    email = current_user['email']

    # Initialize database instances
    db = app.state.mongodb
    today_data_db = TodayDataDB(db)
    hostel_voting_db = HostelVotingDB(db)

    # Check if user has already voted
    has_voted = await hostel_voting_db.check_vote(email, meal_type)
    if has_voted:
        raise HTTPException(status_code=400, detail="You have already voted for this meal type")
    
    # Increment vote in TodayDataDB
    await today_data_db.increment_willing_not_willing(meal_type, will_eat)

    # Insert vote in HostelVotingDB
    await hostel_voting_db.insert_vote(email, meal_type, will_eat)

    return {"message": "Vote successfully recorded"}
    
@app.get("/today_data/", response_model=dict)
async def get_today_data():
    today_data_db = TodayDataDB(app.state.mongodb)
    data = await today_data_db.get_all()
    return data







# CantineMenuDB endpoints
@app.post("/cantine_menu/", response_model=dict)
async def create_cantine_menu_item(item: schemas.CantineMenuItem, ):
    cantine_menu_db = CantineMenuDB(app.state.mongodb)
    inserted_id = await cantine_menu_db.insert_item(item.name, item.description, item.price)
    return {"inserted_id": str(inserted_id)}

@app.put("/cantine_menu/{item_id}", response_model=dict)
async def update_cantine_menu_item(item_id: str, item: schemas.CantineMenuItem, ):
    cantine_menu_db = CantineMenuDB(app.state.mongodb)
    updated_count = await cantine_menu_db.edit_item(item_id, item.name, item.description, item.price)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Item not found or no update needed")
    return {"message": "Item updated"}

@app.delete("/cantine_menu/{item_id}", response_model=dict)
async def delete_cantine_menu_item(item_id: str, ):
    cantine_menu_db = CantineMenuDB(app.state.mongodb)
    deleted_count = await cantine_menu_db.delete_item(item_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

@app.get("/cantine_menu/", response_model=list)
async def read_all_cantine_menu_items():
    cantine_menu_db = CantineMenuDB(app.state.mongodb)
    items = await cantine_menu_db.get_all()
    return items

# HostelMenuDB endpoints
@app.post("/hostel_menu/", response_model=dict)
async def create_hostel_menu_item(item: schemas.HostelMenuItem, ):
    hostel_menu_db = HostelMenuDB(app.state.mongodb)
    inserted_id = await hostel_menu_db.insert_item(item.day, item.name, item.description)
    return {"inserted_id": str(inserted_id)}

@app.put("/hostel_menu/{day}/{item_index}", response_model=dict)
async def update_hostel_menu_item(day: str, item_index: int, item: schemas.HostelMenuItem, ):
    hostel_menu_db = HostelMenuDB(app.state.mongodb)
    updated_count = await hostel_menu_db.edit_item(day, item_index, item.name, item.description)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Item not found or no update needed")
    return {"message": "Item updated"}

@app.delete("/hostel_menu/{day}/{item_index}", response_model=dict)
async def delete_hostel_menu_item(day: str, item_index: int, ):
    hostel_menu_db = HostelMenuDB(app.state.mongodb)
    deleted_count = await hostel_menu_db.delete_item(day, item_index)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

@app.get("/hostel_menu/", response_model=list)
async def read_all_hostel_menu_items():
    hostel_menu_db = HostelMenuDB(app.state.mongodb)
    items = await hostel_menu_db.get_all()
    return items

@app.get("/hostel_menu/{day}", response_model=list)
async def read_day_menu(day: str, ):
    hostel_menu_db = HostelMenuDB(app.state.mongodb)
    menu = await hostel_menu_db.get_day_menu(day)
    return menu
