from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

Users = {
    "Anny": {"Pin": 1234, "balance": 80000},
    "Afsheen": {"Pin": 1111, "balance": 50000},
    "Alishbah": {"Pin": 2222, "balance": 30000}
}

class AuthRequest(BaseModel):
    name: str
    pin_number: int

class DepositRequest(BaseModel):
    name: str
    amount: float

class TransferRequest(BaseModel):
    sender_name: str
    sender_pin: int
    recipient_name: str
    amount: float

@app.get("/")
async def read_root():
    return {"message": "Bank API running"}

@app.post("/authenticate")
async def authenticate_user(request: AuthRequest):
    user_data = Users.get(request.name)
    if not user_data or user_data["Pin"] != request.pin_number:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {"name": request.name, "balance": user_data["balance"]}

@app.post("/deposit")
async def deposit_funds(request: DepositRequest):
    if request.name not in Users:
        raise HTTPException(status_code=404, detail="User not found")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    Users[request.name]["balance"] += request.amount
    return {"name": request.name, "balance": Users[request.name]["balance"]}

@app.post("/bank-transfer")
async def bank_transfer(request: TransferRequest):
    sender_data = Users.get(request.sender_name)
    recipient_data = Users.get(request.recipient_name)

    # 1. Authenticate sender
    if not sender_data or sender_data["Pin"] != request.sender_pin:
        raise HTTPException(status_code=401, detail="Invalid sender credentials")

    # Check if recipient exists
    if not recipient_data:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Check for self-transfer
    if request.sender_name == request.recipient_name:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    # 2. Check if sender has enough balance and amount is positive
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")
    if sender_data["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 3. Subtract amount from sender
    Users[request.sender_name]["balance"] -= request.amount

    # 4. Add amount to recipient
    Users[request.recipient_name]["balance"] += request.amount

    # 5. Return success message
    return {
        "message": "Transfer successful",
        "sender": {"name": request.sender_name, "updated_balance": Users[request.sender_name]["balance"]},
        "recipient": {"name": request.recipient_name, "updated_balance": Users[request.recipient_name]["balance"]}
    }

