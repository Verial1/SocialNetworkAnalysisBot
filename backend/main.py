from fastapi import FastAPI, Depends, HTTPException
from app.db.database import ENGINE, Base, get_db
import app.models.models as models
from contextlib import asynccontextmanager
import asyncio
import app.schemas.schemas as schemas
from app.api import consent, messages
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

app.include_router(consent.router)
app.include_router(messages.router)

@app.get("/")
async def root():
    return {"status": "running", "anonymization": "active"}
