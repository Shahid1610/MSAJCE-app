class TodayDataDB:
    def __init__(self, db_url, ):
        
        self.db = self.client[db_name]
        self.collection = self.db['TodayData']

    async def increment_willing_not_willing(self, meal, willing_increment=0, not_willing_increment=0):
        if meal not in ['breakfast', 'lunch', 'dinner']:
            raise ValueError("Invalid meal type. Choose from 'breakfast', 'lunch', or 'dinner'.")

        update_query = {
            '$inc': {
                f'{meal}.willing': willing_increment,
                f'{meal}.not_willing': not_willing_increment
            }
        }

        result = await self.collection.update_many({}, update_query)
        return result.modified_count

    async def reset_all_data(self):
        update_query = {
            '$set': {
                'breakfast.willing': 0,
                'breakfast.not_willing': 0,
                'lunch.willing': 0,
                'lunch.not_willing': 0,
                'dinner.willing': 0,
                'dinner.not_willing': 0
            }
        }

        result = await self.collection.update_many({}, update_query)
        return result.modified_count

    async def get_all_documents(self):
        cursor = self.collection.find()
        documents = await cursor.to_list(length=None)
        return documents
