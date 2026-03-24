from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class StockMovementCreate(BaseModel):
    productId: str = Field(..., description="MongoDB _id of the product")
    quantity: int = Field(..., gt=0)
    type: Optional[str] = None # IN / OUT

    referenceType: Literal["PURCHASE", "SALE", "MANUAL"] = "MANUAL"
    referenceId: Optional[str] = None

    note: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class StockMovementResponse(StockMovementCreate):
    id: str
    type: str # IN / OUT
