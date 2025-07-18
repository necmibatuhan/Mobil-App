from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import requests
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "debt-tracker-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Enums
class DebtType(str, Enum):
    I_OWE = "i_owe"
    THEY_OWE = "they_owe"

class Currency(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"

class DebtCategory(str, Enum):
    PERSONAL_LOAN = "personal_loan"
    RENT = "rent"
    SHARED_EXPENSE = "shared_expense"
    BUSINESS_LOAN = "business_loan"
    EDUCATION = "education"
    OTHER = "other"

class DebtStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    full_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Debt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    debt_type: DebtType
    person_name: str
    amount: float
    currency: Currency
    amount_in_try: float = 0.0
    description: str
    category: DebtCategory
    status: DebtStatus = DebtStatus.ACTIVE
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

class DebtCreate(BaseModel):
    debt_type: DebtType
    person_name: str
    amount: float
    currency: Currency
    description: str
    category: DebtCategory
    due_date: Optional[datetime] = None

class DebtUpdate(BaseModel):
    person_name: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[Currency] = None
    description: Optional[str] = None
    category: Optional[DebtCategory] = None
    due_date: Optional[datetime] = None

class DashboardStats(BaseModel):
    total_owed: float
    total_to_collect: float
    net_balance: float
    person_owe_most: Optional[str] = None
    person_owe_most_amount: float = 0.0
    most_overdue_debt: Optional[str] = None
    most_overdue_days: int = 0
    active_debts_count: int
    overdue_debts_count: int

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_exchange_rates():
    """Get exchange rates from external API"""
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/TRY")
        if response.status_code == 200:
            rates = response.json()["rates"]
            return {
                "TRY": 1.0,
                "USD": 1.0 / rates["USD"],
                "EUR": 1.0 / rates["EUR"]
            }
    except Exception as e:
        logging.error(f"Error fetching exchange rates: {e}")
    
    # Fallback rates
    return {
        "TRY": 1.0,
        "USD": 34.0,  # Approximate fallback
        "EUR": 37.0   # Approximate fallback
    }

async def convert_to_try(amount: float, currency: str) -> float:
    """Convert amount to TRY"""
    if currency == "TRY":
        return amount
    
    rates = await get_exchange_rates()
    return amount * rates.get(currency, 1.0)

# Authentication Routes
@api_router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Debt Routes
@api_router.post("/debts", response_model=Debt)
async def create_debt(debt_data: DebtCreate, current_user: User = Depends(get_current_user)):
    # Convert amount to TRY
    amount_in_try = await convert_to_try(debt_data.amount, debt_data.currency.value)
    
    debt = Debt(
        user_id=current_user.id,
        debt_type=debt_data.debt_type,
        person_name=debt_data.person_name,
        amount=debt_data.amount,
        currency=debt_data.currency,
        amount_in_try=amount_in_try,
        description=debt_data.description,
        category=debt_data.category,
        due_date=debt_data.due_date
    )
    
    await db.debts.insert_one(debt.dict())
    return debt

@api_router.get("/debts", response_model=List[Debt])
async def get_debts(current_user: User = Depends(get_current_user)):
    debts = await db.debts.find({"user_id": current_user.id}).to_list(1000)
    return [Debt(**debt) for debt in debts]

@api_router.get("/debts/{debt_id}", response_model=Debt)
async def get_debt(debt_id: str, current_user: User = Depends(get_current_user)):
    debt = await db.debts.find_one({"id": debt_id, "user_id": current_user.id})
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return Debt(**debt)

@api_router.put("/debts/{debt_id}", response_model=Debt)
async def update_debt(debt_id: str, debt_data: DebtUpdate, current_user: User = Depends(get_current_user)):
    debt = await db.debts.find_one({"id": debt_id, "user_id": current_user.id})
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    update_data = debt_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # If amount or currency changed, recalculate TRY amount
    if "amount" in update_data or "currency" in update_data:
        amount = update_data.get("amount", debt["amount"])
        currency = update_data.get("currency", debt["currency"])
        update_data["amount_in_try"] = await convert_to_try(amount, currency)
    
    await db.debts.update_one(
        {"id": debt_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_debt = await db.debts.find_one({"id": debt_id, "user_id": current_user.id})
    return Debt(**updated_debt)

@api_router.delete("/debts/{debt_id}")
async def delete_debt(debt_id: str, current_user: User = Depends(get_current_user)):
    result = await db.debts.delete_one({"id": debt_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"message": "Debt deleted successfully"}

@api_router.post("/debts/{debt_id}/mark-paid")
async def mark_debt_paid(debt_id: str, current_user: User = Depends(get_current_user)):
    debt = await db.debts.find_one({"id": debt_id, "user_id": current_user.id})
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    await db.debts.update_one(
        {"id": debt_id, "user_id": current_user.id},
        {"$set": {"status": DebtStatus.PAID, "paid_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Debt marked as paid"}

@api_router.post("/debts/{debt_id}/mark-unpaid")
async def mark_debt_unpaid(debt_id: str, current_user: User = Depends(get_current_user)):
    debt = await db.debts.find_one({"id": debt_id, "user_id": current_user.id})
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    await db.debts.update_one(
        {"id": debt_id, "user_id": current_user.id},
        {"$set": {"status": DebtStatus.ACTIVE, "paid_at": None, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Debt marked as unpaid"}

# Dashboard Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    debts = await db.debts.find({"user_id": current_user.id}).to_list(1000)
    
    total_owed = 0.0
    total_to_collect = 0.0
    person_amounts = {}
    overdue_debts = []
    active_debts_count = 0
    overdue_debts_count = 0
    
    current_date = datetime.utcnow()
    
    for debt_data in debts:
        debt = Debt(**debt_data)
        
        if debt.status == DebtStatus.ACTIVE:
            active_debts_count += 1
            
            if debt.debt_type == DebtType.I_OWE:
                total_owed += debt.amount_in_try
                # Track person I owe most to
                if debt.person_name not in person_amounts:
                    person_amounts[debt.person_name] = 0.0
                person_amounts[debt.person_name] += debt.amount_in_try
            else:
                total_to_collect += debt.amount_in_try
            
            # Check if overdue
            if debt.due_date and debt.due_date < current_date:
                overdue_debts_count += 1
                days_overdue = (current_date - debt.due_date).days
                overdue_debts.append({
                    "description": debt.description,
                    "person": debt.person_name,
                    "days": days_overdue
                })
    
    # Find person I owe most to
    person_owe_most = None
    person_owe_most_amount = 0.0
    if person_amounts:
        person_owe_most = max(person_amounts, key=person_amounts.get)
        person_owe_most_amount = person_amounts[person_owe_most]
    
    # Find most overdue debt
    most_overdue_debt = None
    most_overdue_days = 0
    if overdue_debts:
        most_overdue = max(overdue_debts, key=lambda x: x["days"])
        most_overdue_debt = f"{most_overdue['description']} - {most_overdue['person']}"
        most_overdue_days = most_overdue["days"]
    
    return DashboardStats(
        total_owed=total_owed,
        total_to_collect=total_to_collect,
        net_balance=total_to_collect - total_owed,
        person_owe_most=person_owe_most,
        person_owe_most_amount=person_owe_most_amount,
        most_overdue_debt=most_overdue_debt,
        most_overdue_days=most_overdue_days,
        active_debts_count=active_debts_count,
        overdue_debts_count=overdue_debts_count
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()