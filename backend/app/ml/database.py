"""
SQLite database for storing Dental AI analysis results.

Ukladá výsledky analýz, históriu a export do JSON/CSV.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("/tmp/dental-ai/dental_ai.db")


def _connect() -> sqlite3.Connection:
    """Return a connection; creates parent dirs if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))


def init_db():
    """Initialize SQLite database with required tables."""
    conn = _connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filename TEXT,
            detection_count INTEGER,
            by_class TEXT,
            detections TEXT,
            measurements TEXT,
            health_score REAL,
            notes TEXT,
            image_path TEXT,
            report_path TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            birth_date TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patient_analyses (
            patient_id INTEGER,
            analysis_id TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(job_id: str, data: dict):
    """Save analysis result to database."""
    conn = _connect()
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO analyses
        (id, filename, detection_count, by_class, detections, measurements, health_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        data.get("filename", ""),
        data.get("detection_count", 0),
        json.dumps(data.get("by_class", {})),
        json.dumps(data.get("detections", [])),
        json.dumps(data.get("measurements", [])),
        data.get("health_score", 0.0),
    ))

    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list:
    """Get recent analysis history."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = c.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def export_json(job_id: str) -> dict | None:
    """Export analysis as JSON-parsed dict."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM analyses WHERE id = ?", (job_id,))
    row = c.fetchone()
    conn.close()

    if row:
        result = dict(row)
        for field in ("by_class", "detections", "measurements"):
            if result.get(field):
                result[field] = json.loads(result[field])
        return result
    return None


def export_csv(job_id: str) -> str:
    """Export detections as CSV string."""
    data = export_json(job_id)
    if not data:
        return ""

    lines = ["Tooth,Class,Confidence,Severity,mm"]
    for det in data.get("detections", []):
        tooth = det.get("tooth_number", "?")
        cls_ = det.get("label", "")
        conf = det.get("confidence", 0)
        sev = det.get("severity", "")
        mm = det.get("measurement_mm", "")
        lines.append(f"{tooth},{cls_},{conf:.2f},{sev},{mm}")

    return "\n".join(lines)
