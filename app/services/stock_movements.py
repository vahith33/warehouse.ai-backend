from app.core.database import db
from bson import ObjectId

async def create_stock_movement(data: dict):
    return await db.stock_movements.insert_one(data)

async def list_stock_movements(product_id: str = None):
    query = {}
    if product_id:
        # Match both string and ObjectId versions of the productId
        match_ids = [product_id]
        try:
            if len(product_id) == 24:
                match_ids.append(ObjectId(product_id))
        except:
            pass
        
        query["productId"] = {"$in": match_ids}

    return db.stock_movements.find(query).sort("createdAt", -1)
