from fastapi import APIRouter, HTTPException
from app.schemas.inventory import CurrentStockResponse
from app.utils.mongo import is_valid_object_id
from app.services.products import get_product_by_id
from app.services.inventory import get_current_stock, get_all_inventory

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/current-stock", response_model=CurrentStockResponse)
async def current_stock(productId: str):
    if not is_valid_object_id(productId):
        raise HTTPException(status_code=400, detail="Invalid productId")

    product = await get_product_by_id(productId)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return await get_current_stock(productId)

@router.get("/all")
async def all_inventory():
    return await get_all_inventory()
