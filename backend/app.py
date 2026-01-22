import os
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional, Tuple, List

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error


# ----------------------------
# Config
# ----------------------------
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "boxing")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")

app = Flask(__name__)


# ----------------------------
# Helpers: JSON-safe conversions
# ----------------------------
def to_iso_date(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return str(v)


def to_iso_time(v: Any) -> Optional[str]:
    """
    MySQL TIME can come back as timedelta (mysql-connector), which breaks jsonify.
    Convert to HH:MM:SS string.
    """
    if v is None:
        return None

    if isinstance(v, timedelta):
        total = int(v.total_seconds())
        if total < 0:
            total = 0
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    if isinstance(v, time):
        return v.strftime("%H:%M:%S")

    if isinstance(v, datetime):
        return v.strftime("%H:%M:%S")

    return str(v)


def parse_date_yyyy_mm_dd(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    # keep as string 'YYYY-MM-DD' (MySQL DATE accepts it)
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        return None


def parse_time_hh_mm(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    # accept HH:MM or HH:MM:SS
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            t = datetime.strptime(s, fmt).time()
            return t.strftime("%H:%M:%S")
        except ValueError:
            pass
    return None


def clamp_int(v: Any, default: int, min_v: int = 0, max_v: int = 10**9) -> int:
    try:
        n = int(v)
    except Exception:
        return default
    return max(min_v, min(max_v, n))


def clamp_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


# ----------------------------
# DB
# ----------------------------
def get_conn():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
    )


def q(query: str, params: Tuple = (), fetch: bool = True) -> List[Dict[str, Any]]:
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


def exec_one(query: str, params: Tuple = ()) -> int:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.lastrowid or 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


def ensure_schema():
    """
    Creates tables if missing.
    Keeps your existing 'exercises' table (seeded by init.sql) untouched.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # sessions
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              id INT AUTO_INCREMENT PRIMARY KEY,
              date DATE NOT NULL,
              start_time TIME NULL,
              mode VARCHAR(32) NOT NULL DEFAULT 'boxing',
              intensity VARCHAR(32) NOT NULL DEFAULT 'medium',
              duration_min INT NULL,
              notes TEXT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # session_exercises (typed details)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS session_exercises (
              id INT AUTO_INCREMENT PRIMARY KEY,
              session_id INT NOT NULL,
              type VARCHAR(32) NOT NULL,
              name VARCHAR(255) NOT NULL,

              -- boxing_rounds
              rounds INT NULL,
              round_sec INT NULL,
              rest_sec INT NULL,
              focus VARCHAR(64) NULL,

              -- strength
              sets INT NULL,
              reps INT NULL,
              weight_value DECIMAL(10,2) NULL,
              weight_unit VARCHAR(8) NULL,
              weight_kg DECIMAL(10,2) NULL,

              -- timed
              duration_sec INT NULL,

              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              CONSTRAINT fk_session_exercises_session
                FOREIGN KEY (session_id) REFERENCES sessions(id)
                ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.before_request
def _startup_once():
    # lazy init so container restart stays simple
    if not getattr(app, "_schema_ok", False):
        try:
            ensure_schema()
            app._schema_ok = True
        except Exception:
            # don't crash the whole app; health will show db unknown
            app._schema_ok = False


# ----------------------------
# API
# ----------------------------
@app.get("/api/health")
def health():
    db_state = "unknown"
    try:
        rows = q("SELECT 1 AS ok", fetch=True)
        db_state = "ok" if rows and rows[0].get("ok") == 1 else "unknown"
    except Exception:
        db_state = "unknown"
    return jsonify({"status": "ok", "db": db_state}), 200


@app.get("/api/sessions")
def list_sessions():
    rows = q(
        """
        SELECT id, date, start_time, mode, intensity, duration_min, notes
        FROM sessions
        ORDER BY id DESC
        """
    )

    # ✅ IMPORTANT: convert date/time to JSON-safe strings
    data = []
    for r in rows:
        data.append(
            {
                "id": r["id"],
                "date": to_iso_date(r.get("date")),
                "start_time": to_iso_time(r.get("start_time")),
                "mode": r.get("mode"),
                "intensity": r.get("intensity"),
                "duration_min": r.get("duration_min"),
                "notes": r.get("notes"),
            }
        )
    return jsonify(data), 200


@app.post("/api/sessions")
def create_session():
    payload = request.get_json(force=True, silent=True) or {}

    d = parse_date_yyyy_mm_dd(payload.get("date")) or datetime.utcnow().date().isoformat()
    start_time = parse_time_hh_mm(payload.get("start_time"))
    mode = (payload.get("mode") or "boxing").strip().lower()
    intensity = (payload.get("intensity") or "medium").strip().lower()

    duration_min = payload.get("duration_min", None)
    duration_min = clamp_int(duration_min, default=0, min_v=0) if duration_min is not None else None

    notes = payload.get("notes", None)
    if notes is not None:
        notes = str(notes).strip()
        if notes == "":
            notes = None

    sid = exec_one(
        """
        INSERT INTO sessions (date, start_time, mode, intensity, duration_min, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (d, start_time, mode, intensity, duration_min, notes),
    )

    # Return created session (JSON safe)
    return (
        jsonify(
            {
                "id": sid,
                "date": d,
                "start_time": start_time,
                "mode": mode,
                "intensity": intensity,
                "duration_min": duration_min,
                "notes": notes,
            }
        ),
        201,
    )


@app.delete("/api/sessions/<int:sid>")
def delete_session(sid: int):
    exec_one("DELETE FROM sessions WHERE id=%s", (sid,))
    return jsonify({"ok": True}), 200


@app.get("/api/sessions/<int:sid>/exercises")
def list_session_exercises(sid: int):
    rows = q(
        """
        SELECT
          id, session_id, type, name,
          rounds, round_sec, rest_sec, focus,
          sets, reps, weight_value, weight_unit, weight_kg,
          duration_sec,
          created_at
        FROM session_exercises
        WHERE session_id=%s
        ORDER BY id ASC
        """,
        (sid,),
    )

    # created_at is datetime -> jsonify can handle with str, but keep clean:
    data = []
    for r in rows:
        rr = dict(r)
        if isinstance(rr.get("created_at"), (datetime, date)):
            rr["created_at"] = rr["created_at"].isoformat()
        data.append(rr)

    return jsonify(data), 200


@app.post("/api/sessions/<int:sid>/exercises")
def add_session_exercise(sid: int):
    payload = request.get_json(force=True, silent=True) or {}

    ex_type = (payload.get("type") or "").strip().lower()
    name = (payload.get("name") or "").strip()
    if not ex_type or not name:
        return jsonify({"error": "type and name are required"}), 400

    # defaults
    rounds = round_sec = rest_sec = sets = reps = duration_sec = None
    focus = None
    weight_value = None
    weight_unit = None
    weight_kg = None

    if ex_type == "boxing_rounds":
        rounds = clamp_int(payload.get("rounds"), default=6, min_v=1, max_v=999)
        round_sec = clamp_int(payload.get("round_sec"), default=180, min_v=10, max_v=3600)
        rest_sec = clamp_int(payload.get("rest_sec"), default=60, min_v=0, max_v=3600)
        focus = (payload.get("focus") or "technique").strip().lower()

    elif ex_type == "strength":
        sets = clamp_int(payload.get("sets"), default=4, min_v=1, max_v=999)
        reps = clamp_int(payload.get("reps"), default=8, min_v=1, max_v=999)
        rest_sec = clamp_int(payload.get("rest_sec"), default=90, min_v=0, max_v=3600)

        weight_value = clamp_float(payload.get("weight_value"))
        weight_unit = (payload.get("weight_unit") or "").strip().lower() if weight_value is not None else None
        if weight_unit not in (None, "kg", "lb"):
            weight_unit = None

        if weight_value is not None and weight_unit == "lb":
            weight_kg = float(weight_value) * 0.45359237
        elif weight_value is not None and weight_unit == "kg":
            weight_kg = float(weight_value)
        else:
            weight_kg = None

    elif ex_type == "timed":
        duration_sec = clamp_int(payload.get("duration_sec"), default=600, min_v=10, max_v=24 * 3600)

    else:
        return jsonify({"error": "unknown type"}), 400

    eid = exec_one(
        """
        INSERT INTO session_exercises (
          session_id, type, name,
          rounds, round_sec, rest_sec, focus,
          sets, reps, weight_value, weight_unit, weight_kg,
          duration_sec
        )
        VALUES (%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s,%s, %s)
        """,
        (
            sid,
            ex_type,
            name,
            rounds,
            round_sec,
            rest_sec,
            focus,
            sets,
            reps,
            weight_value,
            weight_unit,
            weight_kg,
            duration_sec,
        ),
    )

    return jsonify({"id": eid, "ok": True}), 201


@app.delete("/api/session_exercises/<int:eid>")
def delete_session_exercise(eid: int):
    exec_one("DELETE FROM session_exercises WHERE id=%s", (eid,))
    return jsonify({"ok": True}), 200


# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    # For Docker: listen on 0.0.0.0
    app.run(host="0.0.0.0", port=5000)
