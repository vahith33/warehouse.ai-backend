from bson import ObjectId

def fix_id(doc: dict) -> dict:
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

def is_valid_object_id(id: str) -> bool:
    return ObjectId.is_valid(id)
