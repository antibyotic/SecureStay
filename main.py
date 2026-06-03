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

@app.get("/agencies")
def get_agencies(): 
   cursor = conn.cursor()
   cursor.execute(
      "SELECT * FROM agencies"
   )
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
def get_agency(id): 
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
