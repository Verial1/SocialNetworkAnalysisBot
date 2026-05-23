from fastapi import FastAPI

app = FastAPI(title="SNA Bot API")

@app.get("/")
def root():
    return {"status": "running", "anonymization": "active"}