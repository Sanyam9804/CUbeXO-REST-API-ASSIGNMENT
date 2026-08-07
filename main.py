# Import Libraries

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


# Ceating object for fastAPI
app = FastAPI()

# Connecting the database
DATABASE_URL = "sqlite:///./account.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Creating Table 
class Account(Base):
    __tablename__ = "Accounts"

    account_number = Column(String, primary_key=True)
    account_holder_name = Column(String, nullable=False)
    initial_balance = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Creating Pydantic table
class AccountCreate(BaseModel):
    account_number: str
    account_holder_name: str
    initial_balance: int

# Route for home
@app.get("/")
def home():
    return {"Message": "Hello User!"}

# Route for creating new account
@app.post("/newAcc")
def newAcc(prod_data: AccountCreate):
    db = SessionLocal()

    existing = db.query(Account).filter(
        Account.account_number == prod_data.account_number
    ).first()

    if existing:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Account Already Exists"
        )

    if prod_data.initial_balance < 0:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Initial Balance cannot be negative"
        )

    new_acc = Account(
        account_number=prod_data.account_number,
        account_holder_name=prod_data.account_holder_name,
        initial_balance=prod_data.initial_balance,
    )

    db.add(new_acc)
    db.commit()
    db.refresh(new_acc)
    db.close()

    return {
        "Message": "Account Created Successfully"
    }


# Route for see the all bank accounts
@app.get("/getAll")
def getAll():
    db = SessionLocal()

    accounts = db.query(Account).all()

    data = [
        {
            "account_number": acc.account_number,
            "account_holder_name": acc.account_holder_name,
            "initial_balance": acc.initial_balance,
        }
        for acc in accounts
    ]

    db.close()

    return data

# Route for getting details by user specific
@app.get("/getDetails/{account_number}")
def getDetails(account_number: str):
    db = SessionLocal()

    details = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if details is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="No Account Found"
        )

    data = {
        "account_number": details.account_number,
        "account_holder_name": details.account_holder_name,
        "initial_balance": details.initial_balance,
    }

    db.close()

    return {
        "Message": "Your Account Details",
        "Data": data
    }

# Route for Deposite Money
@app.put("/deposit/{account_number}/{deposit_amount}")
def deposit(account_number: str, deposit_amount: int):
    db = SessionLocal()

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if account is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="No Account Found"
        )

    if deposit_amount <= 0:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Deposit amount must be greater than zero"
        )

    account.initial_balance += deposit_amount

    db.commit()
    db.refresh(account)

    balance = account.initial_balance

    db.close()

    return {
        "Message": "Successfully Deposited",
        "Current Balance": balance
    }

# Route for withdraw money
@app.put("/withdraw/{account_number}/{withdraw_amount}")
def withdraw(account_number: str, withdraw_amount: int):
    db = SessionLocal()

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if account is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="No Account Found"
        )

    if withdraw_amount <= 0:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Withdraw amount must be greater than zero"
        )

    if withdraw_amount > account.initial_balance:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Insufficient Balance"
        )

    account.initial_balance -= withdraw_amount

    db.commit()
    db.refresh(account)

    balance = account.initial_balance

    db.close()

    return {
        "Message": "Successfully Withdrawn",
        "Current Balance": balance
    }

# Route for delete account
@app.delete("/delete/{account_number}")
def account_delete(account_number: str):
    db = SessionLocal()

    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if account is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="No Account Found"
        )

    db.delete(account)
    db.commit()
    db.close()

    return {
        "Message": "Account Deleted Successfully"
    }

