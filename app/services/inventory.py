from app.core.database import db
from bson import ObjectId

async def get_current_stock(product_id: str):
    # DIRECT RETURN FROM PRODUCT FIELD (NO AGGREGATION NEEDED!)
    # This is much faster and reliable
    product = None
    try:
        # Check both potential ID types
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            product = await db.products.find_one({"id": product_id})
    except:
        pass

    if not product:
        return {
            "productId": product_id,
            "totalIn": 0,
            "totalOut": 0,
            "currentStock": 0,
        }

    # IMPORTANT: We use 0 (integer) instead of "History-derived" to satisfy the Pydantic schema
    return {
        "productId": str(product["_id"]),
        "totalIn": 0, 
        "totalOut": 0,
        "currentStock": int(product.get("currentStock", 0)),
    }

async def get_all_inventory():
    # NEW: Optimized bulk fetch for all products at once
    products = await db.products.find().to_list(1000)
    return [
        {
            "id": str(p["_id"]),
            "sku": p.get("sku"),
            "name": p.get("name"),
            "category": p.get("category"),
            "currentStock": p.get("currentStock", 0),
            "reorderLevel": p.get("reorderLevel", 0),
            "unit": p.get("unit"),
            "isActive": p.get("isActive", True)
        }
        for p in products
    ]
