from fastapi import FastAPI
from database_connection import ENGINE, Base
import models
from periodic_consent_check import check_scheduled
from contextlib import asynccontextmanager
import asyncio
import logging

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Qui defineeremoi cosa succede all'avvio e allo spegnimento
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=ENGINE)
    logger.debug("test1")
    asyncio.create_task(check_scheduled())
    logger.debug("test2")
    yield # Qui l'app rimane accesa e funzionante!!
    
    print("Turning off backend...")

# 2. Inizializziamo l'app passandogli il lifespan
app = FastAPI(title="SNA Bot API", lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}