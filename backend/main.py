from fastapi import FastAPI

app = FastAPI(title="Secure Tax Assistant API", version="1.0.0")

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Secure Tax Assistant API is running"}
