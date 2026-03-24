from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.stock_movements import StockMovementCreate, StockMovementResponse
from app.services import stock_movements as service
from app.services import products as product_service
from app.utils.mongo import fix_id, is_valid_object_id
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/stock-movements", tags=["Stock Movements"])

@router.post("")
async def create_movement(movement: StockMovementCreate, current_user: dict = Depends(get_current_user)):
    # Check if product exists
    if not is_valid_object_id(movement.productId):
        raise HTTPException(status_code=400, detail="Invalid productId")

    product = await product_service.get_product_by_id(movement.productId)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    movement_data = movement.model_dump()
    
    # IMPROVEMENT: If type is explicitly provided by frontend, use it.
    # Otherwise fallback to referenceType mapping.
    if "type" not in movement_data or not movement_data["type"]:
        if movement_data.get("referenceType") == "PURCHASE":
            movement_data["type"] = "IN"
        elif movement_data.get("referenceType") == "SALE":
            movement_data["type"] = "OUT"
        else:
            movement_data["type"] = "IN" # Default for MANUAL or unspecified

    # Ensure upper case
    if "type" in movement_data:
        movement_data["type"] = movement_data["type"].upper()

    result = await service.create_stock_movement(movement_data)
    
    # NEW LOGIC: Atomically update the product currentStock field
    # We add for IN, subtract for OUT
    increment = movement.quantity if movement_data["type"] == "IN" else -movement.quantity
    await product_service.update_product_stock_count(movement.productId, increment)
    
    return {"message": "Movement recorded & stock updated! ⚡", "id": str(result.inserted_id)}

@router.get("", response_model=List[StockMovementResponse])
async def get_movements(productId: str = None, current_user: dict = Depends(get_current_user)):
    movements = []
    cursor = await service.list_stock_movements(productId)
    async for m in cursor:
        movements.append(fix_id(m))
    return movements
