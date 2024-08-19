from motor.motor_asyncio import AsyncIOMotorClient
import secrets


class UserDB:

    def __init__(self, db):
        self.db = db["admin"]["users"]

    async def initialize(self, email):
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

    async def edit_address(self, email, aid, new_address):

        new_address["aid"] = aid

        await self.db.update_one(
            {"email": email, "address_data.aid": aid},
            {"$set": {"address_data.$": new_address}},
        )

    async def add_address(self, email, new_address):

        aid = secrets.token_hex(8)
        new_address["aid"] = aid
        await self.db.update_one(
            {"email": email}, {"$push": {"address_data": new_address}}
        )

    async def remove_address(self, email, aid):

        await self.db.update_one(
            {"email": email}, {"$pull": {"address_data": {"aid": aid}}}
        )

    async def edit_phone(self, email, new_phone):

        await self.db.update_one({"email": email}, {"$set": {"phone": new_phone}})

    async def inc_total_orders(self, email, increment_by):

        result = await self.db.update_one(
            {"email": email},
            {"$inc": {"total_orders": increment_by}},
        )
        print(f"Updated total orders for document with email: {email}")

    async def inc_total_cancel(self, email, increment_by):

        result = await self.db.update_one(
            {"email": email},
            {"$inc": {"total_cancel": increment_by}},
        )
        print(f"Updated total cancel for document with email: {email}")