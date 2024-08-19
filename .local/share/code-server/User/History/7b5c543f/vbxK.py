import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class User:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    async def load_user(self):
        self.user_data = await self.db.users.find_one({"_id": ObjectId(self.user_id)})
        if not self.user_data:
            raise ValueError(f"User with _id {self.user_id} not found")

    async def change_hashed_password(self, email, new_hashed_password):
        if self.user_data["email"] == email:
            await self.db.users.update_one(
                {"_id": ObjectId(self.user_id)},
                {"$set": {"hashed_password": new_hashed_password}}
            )
            self.user_data["hashed_password"] = new_hashed_password
        return self.user_data

    async def add_device(self, email, new_device):
        if self.user_data["email"] == email:
            await self.db.users.update_one(
                {"_id": ObjectId(self.user_id)},
                {"$push": {"device": new_device}}
            )
            self.user_data["device"].append(new_device)
        return self.user_data

    async def remove_device_by_did(self, email, did):
        if self.user_data["email"] == email:
            await self.db.users.update_one(
                {"_id": ObjectId(self.user_id)},
                {"$pull": {"device": {"did": did}}}
            )
            self.user_data["device"] = [
                device for device in self.user_data["device"] if device["did"] != did
            ]
        return self.user_data
