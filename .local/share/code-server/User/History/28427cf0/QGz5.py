def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item["description"],
        "price": item["price"]
    }
class CantineMenuDB:
    def __init__(self, db):
       
        self.db = db['admin']
        self.collection = self.db['cantine_menu']

    async def insert_item(self, name, description, price):
        document = {
            'name': name,
            'description': description,
            'price': price
        }
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def edit_item(self, document_id, name=None, description=None, price=None):
        update_fields = {}
        if name is not None:
            update_fields['name'] = name
        if description is not None:
            update_fields['description'] = description
        if price is not None:
            update_fields['price'] = price

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