from fastapi import FastAPI, Depends, HTTPException
from app.db.database import ENGINE, Base, get_db
import app.models.models as models
from contextlib import asynccontextmanager
import asyncio
import app.schemas.schemas as schemas
from sqlalchemy.orm import Session
#import logging

#logger = logging.getLogger('uvicorn.error')
#logger.setLevel(logging.DEBUG)

# Qui defineeremoi cosa succede all'avvio e allo spegnimento
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=ENGINE)

    yield # Qui l'app rimane accesa e funzionante!!
    
    print("Turning off backend...")

app = FastAPI(title="SNA Bot API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "running", "anonymization": "active"}

# RICORDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA metti le query nelle funzioni crud.py così snelliamo il codice

# --- Endpoint per get_user_servers ---
@app.get("/users/{user_id}/servers")
async def get_user_servers(user_id: str, db: Session = Depends(get_db)):
    # Cerchiamo tutti i server dell'utente nella tabella 'users'
    results = db.query(models.Users.server_id).filter(models.Users.user_id == user_id).all()

    return [r[0] for r in results]

# --- Endpoint per has_already_given_consent ---
@app.get("/consent/check")
async def check_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    exists = db.query(models.Users).filter(
        models.Users.user_id == user_id,
        models.Users.server_id == server_id
    ).first() is not None
    
    return {"exists": exists}

# --- Endpoint per get_latest_id ---
@app.get("/latest_id")
async def latest_id(user_id: str, server_id: str, db: Session = Depends(get_db)):
    res = db.query(models.User_Server).filter(
        models.User_Server.user_id == user_id,
        models.User_Server.server_id == server_id
    ).first()

    if not res:
        raise HTTPException(status_code=404, detail="User/Server relation not found")

    return {
        "latest_id": str(res.latest_message_id) if res.latest_message_id is not None else None
    }

# --- Endpoint per delete_user_data ---
@app.delete("/consent/delete")
async def delete_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    if server_id == "all":
        deleted_count = db.query(models.Users).filter(
            models.Users.user_id == user_id
        ).delete(synchronize_session=False)
        
    else:
        query = db.query(models.Users).filter(
            models.Users.user_id == user_id,
            models.Users.server_id == server_id
        )
        
        if not query.first():
            raise HTTPException(status_code=404, detail="Consent not found for this server")
            
        deleted_count = query.delete(synchronize_session=False)

    db.commit()
    return {"status": "success", "deleted_records": deleted_count}
