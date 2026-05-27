from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
import app.crud.crud as crud

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

@router.get("/latest_id")
async def get_latest_id(user_id: str, server_id: str, db: Session = Depends(get_db)):
    res = crud.get_user_latest_message(user_id = user_id, server_id = server_id, db = db)
    if res == "404":
        raise HTTPException(status_code=404, detail="User/Server relation not found")
    
    return {
        "latest_id": str(res) if res is not None else None
    }