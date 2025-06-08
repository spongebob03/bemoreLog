from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["hello"]
)

@router.get("/hello")
async def hello():
    return {"message": "Hello from FastAPI!"} 