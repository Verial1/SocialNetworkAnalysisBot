from fastapi import FastAPI, Depends
from database_connection import ENGINE, Base, get_db
import models
from contextlib import asynccontextmanager
import asyncio
import schemas
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
def root():
    return {"status": "running", "anonymization": "active"}

# --- Endpoint per get_user_servers ---
@app.get("/users/{user_id}/servers")
def get_user_servers(user_id: str, db: Session = Depends(get_db)):
    # Cerchiamo tutti i server dell'utente nella tabella 'users'
    results = db.query(models.Users.server_id).filter(models.Users.user_id == user_id).all()

    return [r[0] for r in results]

# --- Endpoint per has_already_given_consent ---
@app.get("/consent/check")
def check_consent(user_id: str, server_id: str, db: Session = Depends(get_db)):
    exists = db.query(models.Users).filter(
        models.Users.user_id == user_id,
        models.Users.server_id == server_id
    ).first() is not None
    
    return {"exists": exists}