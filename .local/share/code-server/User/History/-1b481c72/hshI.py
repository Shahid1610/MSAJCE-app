
class UserDB:

    def __init__(self, db):
        self.db = db["admin"]["users"]

    async def initialize(self, email, std_type="hoste"):
        await self.db.insert_one(
            {
                "email": email,
                "voting_data": {
                    "breakfast": False,
                    "lunch": False,
                    "dinner": False
                }
            }
        )

    async def get(self, email):
        data = await self.db.find_one(
            {"email": email},
            {"_id": False}
        )
        return data

    async def update_meal_data(self, email, meal, meal_value):
        if meal not in ['breakfast', 'lunch', 'dinner']:
            raise ValueError("Invalid meal type. Choose from 'breakfast', 'lunch', or 'dinner'.")

        result = await self.db.update_one(
            {'email': email},
            {'$set': {f"voting_data.{meal}": meal_value}}
        )
        return result.modified_count

    async def get_meal_data(self, email, meal):
        if meal not in ['breakfast', 'lunch', 'dinner']:
            raise ValueError("Invalid meal type. Choose from 'breakfast', 'lunch', or 'dinner'.")

        document = await self.db.find_one(
            {'email': email},
            {f'voting_data.{meal}': True, '_id': False}
        )
        if document and 'voting_data' in document:
            return document['voting_data'].get(meal)
        return None
