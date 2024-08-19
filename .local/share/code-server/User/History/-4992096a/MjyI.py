class MealDB:
    def __init__(self, uri, db_name, collection_name):
        # Connect to MongoDB using Motor
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def insert_data(self, key, email, meal_type, will_eat):
        # Insert a new document into the collection
        document = {
            "key": key,
            "email": email,
            "meal_type": meal_type,
            "will_eat": will_eat
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