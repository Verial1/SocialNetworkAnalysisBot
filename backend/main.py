from fastapi import FastAPI
from database import engine, Base
import models

Base.metadata.create_all(bind=engine)
print("Tables succesfully created!")

app = FastAPI(title="SNA Bot API")

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}