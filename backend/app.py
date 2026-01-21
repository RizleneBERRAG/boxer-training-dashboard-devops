import os
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "boxer"),
        password=os.environ.get("DB_PASSWORD", "boxerpass"),
        database=os.environ.get("DB_NAME", "boxing"),
    )

def ensure_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            duration_min INT NOT NULL,
            intensity VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    cur.close()

@app.get("/api/health")
def health():
    return jsonify(status="ok")

@app.get("/api/sessions")
def list_sessions():
    conn = get_db()
    ensure_table(conn)

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, date, duration_min, intensity FROM sessions ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

@app.post("/api/sessions")
def create_session():
    data = request.get_json(silent=True) or {}

    date = data.get("date", "2026-01-21")
    duration_min = int(data.get("duration_min", 60))
    intensity = data.get("intensity", "medium")

    conn = get_db()
    ensure_table(conn)

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (date, duration_min, intensity) VALUES (%s, %s, %s)",
        (date, duration_min, intensity),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify(id=new_id, date=date, duration_min=duration_min, intensity=intensity), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
