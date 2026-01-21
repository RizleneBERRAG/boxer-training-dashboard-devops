import os
import mysql.connector
from flask import Flask, jsonify

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "boxer"),
        password=os.environ.get("DB_PASSWORD", "boxerpass"),
        database=os.environ.get("DB_NAME", "boxing"),
    )

@app.get("/api/health")
def health():
    return jsonify(status="ok")

@app.get("/api/sessions")
def list_sessions():
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                duration_min INT NOT NULL,
                intensity VARCHAR(20) NOT NULL
            )
        """)
        cur.execute("SELECT id, date, duration_min, intensity FROM sessions ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
