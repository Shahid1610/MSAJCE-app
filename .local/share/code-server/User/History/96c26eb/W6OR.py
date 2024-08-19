class HostelMenuDB:
    def __init__(self, db):
        self.collection = db['hostel_menu']

    async def insert_item(self, day, name, description):
        document = {
            'name': name,
            'description': description
        }
        result = await self.collection.update_one(
            {day: {'$exists': True}},
            {'$push': {day: document}},
            upsert=True
        )
        return result.upserted_id or result.modified_count

    async def edit_item(self, day, item_index, name=None, description=None):
        update_fields = {}
        if name is not None:
            update_fields[f'{day}.$[{item_index}].name'] = name
        if description is not None:
            update_fields[f'{day}.$[{item_index}].description'] = description

        if update_fields:
            result = await self.collection.update_one(
                {day: {'$exists': True}},
                {'$set': update_fields}
            )
            return result.modified_count
        else:
            return 0

    async def delete_item(self, day, item_index):
        result = await self.collection.update_one(
            {day: {'$exists': True}},
            {'$unset': {f'{day}.{item_index}': 1}}
        )
        await self.collection.update_one(
            {day: {'$exists': True}},
            {'$pull': {day: None}}
        )
        return result.modified_count

    async def get_all(self):
        cursor = self.collection.find()
        documents = await cursor.to_list(length=None)
        return documents

    async def get_day_menu(self, day):
        document = await self.collection.find_one(
            {day: {'$exists': True}},
            {day: True, '_id': False}
        )
        return document.get(day, []) if document else []