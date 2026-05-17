from fastapi import FastAPI
from database import engine, Base
import models

app = FastAPI(title="SNA Bot API")

Base.metadata.create_all(bind=engine)
print("Tables succesfully created!")

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}