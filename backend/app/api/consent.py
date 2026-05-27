from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
import app.crud.crud as crud  # Supponendo che sposti qui le query

router = APIRouter(
    prefix="/consent",
    tags=["Consent & Users"]
)

@router.get("/check")
async def check_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    exists = crud.get_user_consent(user_id = user_id, server_id = server_id, db = db)
    return {"exists": exists}

@router.get("/{user_id}/servers")
async def get_user_servers(user_id: str, db: Session = Depends(get_db)):
    return crud.get_user_servers(user_id = user_id, db = db)

@router.delete("/delete")
async def delete_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    res = crud.remove_consent(user_id = user_id,server_id = server_id, db = db)
    if res == "404":
        raise HTTPException(status_code=404, detail="Consent not found")
    return {"status": res}