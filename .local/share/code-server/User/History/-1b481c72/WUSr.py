from motor.motor_asyncio import AsyncIOMotorClient
import secrets


class UserDB:

    def __init__(self, db):
        self.db = db["admin"]["users"]

    async def initialize(self, email,std_type = "hoste"):
        await self.db.insert_one(
            {
                "email": email,

            }
        )

    async def get(self,email):
        data = await self.db.find_one(
            {"email": email},
            {"_id": False}
        )
        return data

   