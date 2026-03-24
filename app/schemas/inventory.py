from pydantic import BaseModel

class CurrentStockResponse(BaseModel):
    productId: str
    totalIn: int
    totalOut: int
    currentStock: int
