import uuid

def generate_id():
    return str(uuid.uuid4())

def find_item_by_uuid(database, uuid):
    for item in database:
        if item['uuid'] == uuid:
            return item
    return None