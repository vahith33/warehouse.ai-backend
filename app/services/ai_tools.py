from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.core.database import db
from bson import ObjectId


async def get_low_stock_products() -> List[Dict[str, Any]]:
    """Return products where current stock is less than or equal to the reorder level.

    The query uses an aggregation pipeline to join with the stock_movements
    collection, compute total IN and OUT quantities and then filter by
    ``reorderLevel``. Documents returned are JSON-serializable (ObjectId are
    converted to str).
    """
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "stock_movements",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$productId", "$$pid"]}
                            }
                        },
                        {"$group": {"_id": "$type", "qty": {"$sum": "$quantity"}}},
                    ],
                    "as": "movement_summaries",
                }
            },
            {
                "$addFields": {
                    "totalIn": {
                        "$sum": {
                            "$map": {
                                "input": "$movement_summaries",
                                "as": "m",
                                "in": {
                                    "$cond": [
                                        {"$eq": ["$$m._id", "IN"]},
                                        "$$m.qty",
                                        0,
                                    ]
                                },
                            }
                        }
                    },
                    "totalOut": {
                        "$sum": {
                            "$map": {
                                "input": "$movement_summaries",
                                "as": "m",
                                "in": {
                                    "$cond": [
                                        {"$eq": ["$$m._id", "OUT"]},
                                        "$$m.qty",
                                        0,
                                    ]
                                },
                            }
                        }
                    },
                }
            },
            {
                "$addFields": {
                    "currentStock": {"$subtract": ["$totalIn", "$totalOut"]}
                }
            },
            {"$match": {"$expr": {"$lte": ["$currentStock", {"$ifNull": ["$reorderLevel", 0]}]}}},
            {"$project": {"sku": 1, "name": 1, "currentStock": 1, "reorderLevel": 1}},
        ]

        cursor = db.products.aggregate(pipeline)
        results: List[Dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    except Exception:  # pragma: no cover - fallback in case of Mongo error
        return []


async def get_product_inventory(product_name: str) -> Dict[str, Any] | None:
    """Return current stock for a product identified by name or SKU.

    A case-insensitive regex is used for matching. The same stock calculation
    pipeline as ``get_low_stock_products`` is applied, but restricted to the
    matching product.
    """
    try:
        regex = {"$regex": product_name, "$options": "i"}
        pipeline = [
            {
                "$match": {"$or": [{"name": regex}, {"sku": regex}]}
            },
            {
                "$lookup": {
                    "from": "stock_movements",
                    "let": {"pid": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$productId", "$$pid"]}
                            }
                        },
                        {"$group": {"_id": "$type", "qty": {"$sum": "$quantity"}}},
                    ],
                    "as": "movement_summaries",
                }
            },
            {
                "$addFields": {
                    "totalIn": {
                        "$sum": {
                            "$map": {
                                "input": "$movement_summaries",
                                "as": "m",
                                "in": {
                                    "$cond": [
                                        {"$eq": ["$$m._id", "IN"]},
                                        "$$m.qty",
                                        0,
                                    ]
                                },
                            }
                        }
                    },
                    "totalOut": {
                        "$sum": {
                            "$map": {
                                "input": "$movement_summaries",
                                "as": "m",
                                "in": {
                                    "$cond": [
                                        {"$eq": ["$$m._id", "OUT"]},
                                        "$$m.qty",
                                        0,
                                    ]
                                },
                            }
                        }
                    },
                }
            },
            {
                "$addFields": {
                    "currentStock": {"$subtract": ["$totalIn", "$totalOut"]}
                }
            },
            {"$project": {"sku": 1, "name": 1, "currentStock": 1}},
            {"$limit": 1},
        ]
        cursor = db.products.aggregate(pipeline)
        doc = await cursor.to_list(length=1)
        if not doc:
            return None
        record = doc[0]
        record["_id"] = str(record["_id"])
        return record
    except Exception:  # pragma: no cover
        return None


async def get_today_stock_movements() -> List[Dict[str, Any]]:
    """Return all IN/OUT movements that were created today (UTC).

    The ``createdAt`` field is expected to be a Python ``datetime`` stored in
    Mongo; it is serialized to ISO format before returning.
    """
    try:
        start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        cursor = db.stock_movements.find({"createdAt": {"$gte": start, "$lt": end}})
        results: List[Dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["productId"] = str(doc.get("productId"))
            if isinstance(doc.get("createdAt"), datetime):
                doc["createdAt"] = doc["createdAt"].isoformat()
            results.append(doc)
        return results
    except Exception:  # pragma: no cover
        return []


async def search_products_by_name(name: str) -> List[Dict[str, Any]]:
    """Return products whose name or SKU contains ``name`` (case-insensitive)."""
    try:
        regex = {"$regex": name, "$options": "i"}
        cursor = db.products.find({"$or": [{"name": regex}, {"sku": regex}]})
        results: List[Dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    except Exception:  # pragma: no cover
        return []
