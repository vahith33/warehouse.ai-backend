from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.products import ProductCreate, ProductResponse
from app.services import products as service
from app.utils.mongo import fix_id, is_valid_object_id
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("")
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    # Check duplicate SKU
    existing = await service.get_product_by_sku(product.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    # Check duplicate barcode
    if product.barcode:
        existing_barcode = await service.get_product_by_barcode(product.barcode)
        if existing_barcode:
            raise HTTPException(status_code=400, detail="Barcode already exists")

    result = await service.create_product(product.model_dump())
    return {"message": "Product created ✅", "id": str(result.inserted_id)}

@router.get("", response_model=List[ProductResponse])
async def get_products(current_user: dict = Depends(get_current_user)):
    products = []
    cursor = await service.list_products()
    async for p in cursor:
        products.append(fix_id(p))
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, current_user: dict = Depends(get_current_user)):
    if not is_valid_object_id(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return fix_id(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, 
    data: ProductCreate, 
    current_user: dict = Depends(get_current_user)
):
    if not is_valid_object_id(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    
    # Check if SKU changed and is taken
    existing = await service.get_product_by_sku(data.sku)
    if existing and str(existing["_id"]) != product_id:
        raise HTTPException(status_code=400, detail="SKU already used by another product")

    updated = await service.update_product(product_id, data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return fix_id(updated)

@router.delete("/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    if not is_valid_object_id(product_id):
        raise HTTPException(status_code=400, detail="Invalid product id")
    
    result = await service.delete_product(product_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found or already deleted")
    
    return {"message": "Product deleted 🗑️"}
