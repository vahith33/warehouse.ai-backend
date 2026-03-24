from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "WareHouseDetails")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI missing in backend/.env file")
