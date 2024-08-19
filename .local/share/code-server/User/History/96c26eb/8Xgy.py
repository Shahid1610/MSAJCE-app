class HostelMenuDB:
    def __init__(self, db):
        self.collection = db['hostel_menu']

    async def insert_item(self, name, description):
        document = {
            'name': name,
            'description': description
        }
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def edit_item(self, document_id, name=None, description=None):
        update_fields = {}
        if name is not None:
            update_fields['name'] = name
        if description is not None:
            update_fields['description'] = description

        if update_fields:
            result = await self.collection.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': update_fields}
            )
            return result.modified_count
        else:
            return 0

    async def delete_item(self, document_id):
        result = await self.collection.delete_one(
            {'_id': ObjectId(document_id)}
        )
        return result.deleted_count

    async def get_all(self):
        cursor = self.collection.find()
        documents = await cursor.to_list(length=None)
        return documents
