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
    async def update_breakfast(email, breakfast_value):
        result = await collection.update_one(
            {'email': email},  # filter by email
            {'$set': {'voting_data.breakfast': breakfast_value}}  # update the breakfast field within voting_data
        )
        return result.modified_count
    
    async def update_breakfast(email, breakfast_value):
        result = await collection.update_one(
            {'email': email},  # filter by email
            {'$set': {'voting_data.breakfast': breakfast_value}}  # update the breakfast field within voting_data
        )
        return result.modified_count

async def update_breakfast(email, breakfast_value):
        result = await collection.update_one(
            {'email': email},  # filter by email
            {'$set': {'voting_data.breakfast': breakfast_value}}  # update the breakfast field within voting_data
        )
        return result.modified_count


    