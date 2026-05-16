from fastapi import FastAPI, Depends
from database import engine, Base
import models

# Crea le tabelle all'avvio
print("Creazione tabelle in corso...")
Base.metadata.create_all(bind=engine)
print("Tabelle create con successo!")

app = FastAPI(title="SNA Bot API")

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}