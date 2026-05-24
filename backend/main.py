from fastapi import FastAPI
from database_connection import ENGINE, Base
import models

Base.metadata.create_all(bind=ENGINE)
app = FastAPI(title="SNA Bot API")

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}