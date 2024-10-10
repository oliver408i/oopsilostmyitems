import uuid

def generate_id():
    return str(uuid.uuid4())

def find_item_by_uuid(database, uuid):
    for item in database:
        if database[item]['uuid'] == uuid:
            return database[item]
    return None