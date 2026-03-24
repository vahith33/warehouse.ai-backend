from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(..., min_length=2, max_length=100)

    brand: Optional[str] = None
    unit: str = Field(..., description="pcs / kg / ltr etc")
    barcode: Optional[str] = None

    costPrice: float = Field(..., ge=0)
    sellingPrice: float = Field(..., ge=0)
    reorderLevel: int = Field(0, ge=0)
    currentStock: float = Field(0, description="Real-time stock level")

    isActive: bool = True

class ProductResponse(ProductCreate):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
