import psycopg2
import os
from fastapi import FastAPI 
from dotenv import load_dotenv

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