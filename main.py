import psycopg2
import os
from fastapi import FastAPI 
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

app = FastAPI()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_admin(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user

def require_staff(current_user = Depends(get_current_user)):
    if current_user["role"] not in ["mitarbeiter","admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

@app.get("/health")
def health_check():
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    return {"status": "Datenbankverbindung erfolgreich"}

class AgencyCreate(BaseModel):
    name: str
    domain: str
    email: str
    phone: str 
    address: str 

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    agency_id: Optional[int] = None 
    



@app.post("/agencies")
def create_agency(agency:AgencyCreate, current_user = Depends(require_admin)):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agencies (name, domain, email, phone, address, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
        (agency.name, agency.domain, agency.email, agency.phone, agency.address)
    )
    conn.commit()
    return {"message": "Agentur erfolgreich erstellt"}

@app.get("/agencies")
def get_agencies(current_user = Depends(require_staff)): 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agencies")
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "domain": row[2],
            "email": row[3],
            "phone": row[4],
            "address": row[5],
            "created_at": row[6]
        }
        for row in rows
    ]

@app.get("/agencies/{id}")
def get_agency(id, current_user = Depends(require_staff)): 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agencies WHERE id = %s", (id,))
    row = cursor.fetchone()
    return {
                "id": row[0],
                "name": row[1],
                "domain": row[2],
                "email": row[3],
                "phone": row[4],
                "address": row[5],
                "created_at": row[6]
    }

@app.post("/register")
def register_user(user: UserCreate):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role, agency_id, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
        (user.name, user.email, hashed, "kunde", user.agency_id, True)
    )
    conn.commit()
    return {"message": "User erfolgreich registriert"}
    


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(request: LoginRequest): 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (request.email,))
    user = cursor.fetchone()

    if not user:
        return {"error": "Invalid credentials"}

    stored_hash = user[3]
    if not bcrypt.checkpw(request.password.encode(), stored_hash.encode()):
        return {"error": "Invalid credentials"}
    
    token = jwt.encode(
        {"user_id": user[0], "role": user[4], "exp": datetime.utcnow() + timedelta(hours=1)},
        os.getenv("JWT_SECRET"), 
        algorithm="HS256"
    )

    return {"token": token}