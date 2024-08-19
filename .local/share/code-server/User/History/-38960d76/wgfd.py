import motor.motor_asyncio
import asyncio

class MetaData:
    def __init__(self, db):
        self.db = db["admin"]
        self.collection = self.db["meta_data"]

    async def insert_data(self, email, meal_type, will_eat, will_not_eat):
        # Insert a new document into the collection
        document = {
            "email": email,
            "meal_type": meal_type,
            "will_eat": will_eat,
            "will_not_eat": will_not_eat
        }
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def get_data_by_email_and_meal_type(self, email, meal_type):
        # Find a document by email and meal_type
        query = {"email": email, "meal_type": meal_type}
        document = await self.collection.find_one(query)
        return document

    async def get_all_meal_types(self):
        # Find all distinct meal_types
        meal_types = await self.collection.distinct("meal_type")
        return meal_types

    async def get_data_by_will_eat(self, will_eat):
        # Find all documents where will_eat matches
        query = {"will_eat": will_eat}
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return documents

    async def increment_will_eat(self, email, meal_type, amount=1):
        # Increment the will_eat field
        query = {"email": email, "meal_type": meal_type}
        update = {"$inc": {"will_eat": amount}}
        result = await self.collection.update_one(query, update)
        return result.modified_count

    async def decrement_will_eat(self, email, meal_type, amount=1):
        # Decrement the will_eat field
        query = {"email": email, "meal_type": meal_type}
        update = {"$inc": {"will_eat": -amount}}
        result = await self.collection.update_one(query, update)
        return result.modified_count

    async def increment_will_not_eat(self, email, meal_type, amount=1):
        # Increment the will_not_eat field
        query = {"email": email, "meal_type": meal_type}
        update = {"$inc": {"will_not_eat": amount}}
        result = await self.collection.update_one(query, update)
        return result.modified_count

    async def decrement_will_not_eat(self, email, meal_type, amount=1):
        # Decrement the will_not_eat field
        query = {"email": email, "meal_type": meal_type}
        update = {"$inc": {"will_not_eat": -amount}}
        result = await self.collection.update_one(query, update)
        return result.modified_count

    async def update_meal_count(self, data_type, time_of_day, total_will_eat_delta=0, total_will_not_eat_delta=0):
        # Update total_will_eat and total_will_not_eat based on data_type and time_of_day
        query = {"data_type": data_type}
        update = {
            "$inc": {
                f"meal_type.{time_of_day}.total_will_eat": total_will_eat_delta,
                f"meal_type.{time_of_day}.total_will_not_eat": total_will_not_eat_delta
            }
        }
        result = await self.collection.update_one(query, update)
        return result.modified_count

#