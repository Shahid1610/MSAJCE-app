
class HostelVotingDB:
    def __init__(self, db):
        self.collection = db['hostel_voting']

    async def insert_vote(self, email, meal_type, will_eat):
        document = {
            'email': email,
            'meal_type': meal_type,
            'will_eat': will_eat
        }
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def delete_all_votes(self):
        result = await self.collection.delete_many({})
        return result.deleted_count

    async def get_all_votes(self):
        cursor = self.collection.find()
        documents = await cursor.to_list(length=None)
        return documents
    async def check_vote(self, email, meal_type):
        result = await self.collection.find_one(
            {'email': email, 'meal_type': meal_type},
            {'_id': False}
        )
        return result is not None