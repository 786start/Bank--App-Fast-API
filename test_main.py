from fastapi.testclient import TestClient
from main import app, Users

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bank API running"}

def test_authenticate_success():
    response = client.post(
        "/authenticate",
        json={"name": "Anny", "pin_number": 1234}
    )
    assert response.status_code == 200
    assert response.json() == {"name": "Anny", "balance": 80000}

def test_authenticate_invalid_credentials():
    response = client.post(
        "/authenticate",
        json={"name": "Anny", "pin_number": 9999}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials"}

    response = client.post(
        "/authenticate",
        json={"name": "NonExistentUser", "pin_number": 1234}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials"}

def test_deposit_success():
    # Store initial balance to verify changes
    initial_balance = Users["Afsheen"]["balance"]
    deposit_amount = 1000.0

    response = client.post(
        "/deposit",
        json={"name": "Afsheen", "amount": deposit_amount}
    )
    assert response.status_code == 200
    assert response.json() == {"name": "Afsheen", "balance": initial_balance + deposit_amount}
    assert Users["Afsheen"]["balance"] == initial_balance + deposit_amount

def test_deposit_user_not_found():
    response = client.post(
        "/deposit",
        json={"name": "NonExistentUser", "amount": 100.0}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_deposit_negative_amount():
    response = client.post(
        "/deposit",
        json={"name": "Anny", "amount": -100.0}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Deposit amount must be positive"}

def test_bank_transfer_success():
    initial_sender_balance = Users["Anny"]["balance"]
    initial_recipient_balance = Users["Alishbah"]["balance"]
    transfer_amount = 5000.0

    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 1234,
            "recipient_name": "Alishbah",
            "amount": transfer_amount
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Transfer successful",
        "sender": {"name": "Anny", "updated_balance": initial_sender_balance - transfer_amount},
        "recipient": {"name": "Alishbah", "updated_balance": initial_recipient_balance + transfer_amount}
    }
    assert Users["Anny"]["balance"] == initial_sender_balance - transfer_amount
    assert Users["Alishbah"]["balance"] == initial_recipient_balance + transfer_amount

def test_bank_transfer_invalid_sender_credentials():
    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 9999,
            "recipient_name": "Alishbah",
            "amount": 100.0
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid sender credentials"}

def test_bank_transfer_recipient_not_found():
    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 1234,
            "recipient_name": "NonExistentRecipient",
            "amount": 100.0
        }
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Recipient not found"}

def test_bank_transfer_self_transfer():
    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 1234,
            "recipient_name": "Anny",
            "amount": 100.0
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot transfer to the same account"}

def test_bank_transfer_negative_amount():
    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 1234,
            "recipient_name": "Alishbah",
            "amount": -100.0
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Transfer amount must be positive"}

def test_bank_transfer_insufficient_funds():
    response = client.post(
        "/bank-transfer",
        json={
            "sender_name": "Anny",
            "sender_pin": 1234,
            "recipient_name": "Alishbah",
            "amount": 999999.0 # More than Anny's balance
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient funds"}
