from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db
import app.crud.crud as crud  # Supponendo che sposti qui le query

router = APIRouter(
    prefix="/consent",
    tags=["Consent & Users"]
)

@router.get("/check")
async def check_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    res = crud.get_user_consent(user_id = user_id, server_id = server_id, db = db)
    return {"exists": res is not None}

@router.get("/{user_id}/servers")
async def get_user_servers(user_id: str, db: Session = Depends(get_db)):
    return crud.get_user_servers(user_id = user_id, db = db)

@router.delete("/delete")
async def delete_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    try:
        success = crud.remove_consent(user_id = user_id,server_id = server_id, db = db)
        if not success:
            raise HTTPException(status_code=404, detail="Consent not found")
        
        db.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Database Error")