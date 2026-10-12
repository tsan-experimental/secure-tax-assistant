from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Secure Tax Assistant API")

# Configure CORS so your React frontend can communicate with FastAPI
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Secure Tax Assistant Backend API Connected!"}

@app.get("/calculate-tax/")
def calculate_tax(income: float, rate: float = 0.15):
    """
    Calculate simple tax based on income and a tax rate.
    """
    tax_owed = income * rate
    return {
        "income": income,
        "tax_rate": rate,
        "tax_owed": tax_owed
    }