import psycopg2
import os
from fastapi import FastAPI 
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

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

@app.post("/agencies")
def create_agency(agency:AgencyCreate):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agencies (name, domain, email, phone, address, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
        (agency.name, agency.domain, agency.email, agency.phone, agency.address)
    )
    conn.commit()
    return {"message": "Agentur erfolgreich erstellt"}
