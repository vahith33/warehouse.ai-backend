from app.core.database import db
from bson import ObjectId

async def create_product(data: dict):
    return await db.products.insert_one(data)

async def list_products():
    return db.products.find().sort("name", 1)

async def get_product_by_id(product_id: str):
    return await db.products.find_one({"_id": ObjectId(product_id)})

async def update_product(product_id: str, data: dict):
    await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
    return await get_product_by_id(product_id)

async def delete_product(product_id: str):
    return await db.products.delete_one({"_id": ObjectId(product_id)})

async def get_product_by_sku(sku: str):
    return await db.products.find_one({"sku": sku})

async def get_product_by_barcode(barcode: str):
    return await db.products.find_one({"barcode": barcode})

# NEW: Atomic increment/decrement of stock count
async def update_product_stock_count(product_id: str, increment: float):
    return await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$inc": {"currentStock": increment}}
    )
