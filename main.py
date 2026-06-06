import psycopg2
import os
from fastapi import FastAPI 
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


load_dotenv()

app = FastAPI()

security = HTTPBearer()

# Authorization & Authentication

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

# Health Check

@app.get("/health")
def health_check():
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    return {"status": "Datenbankverbindung erfolgreich"}

# Models

class AgencyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    domain: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    phone: str = Field(min_length=5, max_length=20)
    address: str = Field(min_length=5, max_length=200)

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8)
    agency_id: Optional[int] = None
    
class PropertyCreate(BaseModel):
    address: str = Field(min_length=5, max_length=200)
    size_sqm: float = Field(gt=0)
    monthly_price: float = Field(gt=0)
    agency_id: int = Field(gt=0)

class BookingCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    property_id: int = Field(gt=0)

# Agency Endpoints

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

# Property Endpoints

@app.post("/properties")
def create_property(property: PropertyCreate, current_user = Depends(require_staff)):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO properties (address, size_sqm, monthly_price, agency_id, is_occupied, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
        (property.address, property.size_sqm, property.monthly_price, property.agency_id, False)
    )
    conn.commit()
    return {"message": "Immobilie erfolgreich erstellt"}

@app.get("/properties")
def get_properties(current_user = Depends(get_current_user)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties")
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "address": row[1],
            "size_sqm": row[2],
            "monthly_price": row [3],
            "agency_id": row[4],
            "is_occupied": row[5],
            "created_at": row[6]
        } for row in rows
    ]

@app.get("/properties/{id}")
def get_property(id, current_user = Depends(get_current_user)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE id = %s", (id,))
    row = cursor.fetchone()
    return {
            "id": row[0],
            "address": row[1],
            "size_sqm": row[2],
            "monthly_price": row [3],
            "agency_id": row[4],
            "is_occupied": row[5],
            "created_at": row[6]
        }

@app.delete("/properties/{id}")
def delete_property(id: int, current_user = Depends(require_staff)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id = %s", (id,))
    conn.commit()
    return {"message": "Immobilie erfolgreich gelöscht"}
    
# Booking Endpoints

@app.post("/bookings")
def create_booking(booking: BookingCreate, current_user = Depends(get_current_user)):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (start_date, end_date, property_id, user_id, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (booking.start_date, booking.end_date, booking.property_id, current_user["user_id"])
    )
    conn.commit()
    return {"message": "Buchung erfolgreich erstellt"}

@app.get("/bookings")
def get_bookings(current_user = Depends(require_staff)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "start_date": row[1],
            "end_date": row[2],
            "property_id": row[3],
            "user_id": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]
@app.get("/bookings/me")
def get_my_bookings(current_user = Depends(get_current_user)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (current_user["user_id"],))
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "start_date": row[1],
            "end_date": row[2],
            "property_id": row[3],
            "user_id": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]

@app.delete("/bookings/{id}")
def delete_booking(id: int, current_user = Depends(require_admin)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = %s", (id,))
    conn.commit()
    return {"message": "Buchung erfolgreich gelöscht"}

# User Endpoints

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
    
@app.delete("/users/{id}")
def deactivate_user(id: int, current_user = Depends(require_admin)):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = false WHERE id = %s", (id,))
    conn.commit()
    return {"message": "User erfolgreich deaktiviert"}


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