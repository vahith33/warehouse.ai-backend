from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import db
from app.core.dependencies import get_current_user

from app.routes.products import router as products_router
from app.routes.stock_movements import router as stock_router
from app.routes.inventory import router as inventory_router
from app.routes.auth import router as auth_router
from app.routes.ai import router as ai_router

app = FastAPI(title="Warehouse Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "FastAPI is running 🚀"}


@app.get("/db-test")
async def db_test():
    try:
        collections = await db.list_collection_names()
        return {
            "status": "ok",
            "message": "MongoDB connected successfully ✅",
            "collections": collections,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


app.include_router(products_router, dependencies=[Depends(get_current_user)])
app.include_router(stock_router, dependencies=[Depends(get_current_user)])
app.include_router(inventory_router, dependencies=[Depends(get_current_user)])
app.include_router(auth_router)
app.include_router(ai_router, dependencies=[Depends(get_current_user)])
