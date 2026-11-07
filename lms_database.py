"""
========================================================================================
VoltCore Apex Academia - LMS Database Engine
Tailored for Anna University / MIT Campus Standards (Department of Electronics Eng.)
----------------------------------------------------------------------------------------
Module: lms_database.py
Platform Lead / Architect: Ashok Kumar A (ashokkumar2008313@gmail.com | +91 9597382878)
GitHub Profile: https://github.com/AshokKumar313 (Username: AshokKumar313)
Security Standard: OWASP Compliant PBKDF2-HMAC-SHA256 (Upgraded to 600,000 Iterations)
Architecture: Thread-safe SQLite relational database with Foreign Key enforcement
========================================================================================
"""

import os
import sqlite3
import hashlib
import hmac
import secrets
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# Configuration Constants
DB_FILE: str = os.environ.get("LMS_DB_PATH", "voltcore_lms.db")
HASH_ALGORITHM: str = "sha256"
PBKDF2_ITERATIONS: int = 600_000
SALT_BYTE_LENGTH: int = 16


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """
    Establish a thread-safe connection to the SQLite database with Foreign Keys enabled
    and standard WAL performance configurations enforced.
    Returns sqlite3.Row mapped connection for dictionary-like column access.
    """
    conn = sqlite3.connect(db_path, timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """
    Generate an OWASP-compliant PBKDF2-HMAC-SHA256 password hash.
    Format: pbkdf2_sha256$260000$<salt_hex>$<hash_hex>
    
    :param password: Plaintext password string
    :param salt: Optional 16-byte cryptographically secure salt. If None, generated via secrets.
    :return: Formatted hash string
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    if salt is None:
        salt = secrets.token_bytes(SALT_BYTE_LENGTH)
    elif len(salt) < 16:
        raise ValueError("Salt must be at least 16 bytes for cryptographic security.")

    derived_key = hashlib.pbkdf2_hmac(
        hash_name=HASH_ALGORITHM,
        password=password.encode("utf-8"),
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        dklen=32  # 256 bits output
    )

    salt_hex = salt.hex()
    hash_hex = derived_key.hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_hex}${hash_hex}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2-HMAC-SHA256 hash using constant-time comparison.
    
    :param password: Plaintext password to verify
    :param stored_hash: Stored formatted hash string
    :return: True if valid, False otherwise
    """
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4:
            return False

        algo, iterations_str, salt_hex, hash_hex = parts
        if algo != "pbkdf2_sha256":
            return False

        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        computed_key = hashlib.pbkdf2_hmac(
            hash_name=HASH_ALGORITHM,
            password=password.encode("utf-8"),
            salt=salt,
            iterations=iterations,
            dklen=len(expected_hash)
        )

        return hmac.compare_digest(computed_key, expected_hash)
    except Exception:
        return False


def init_db(db_path: str = DB_FILE) -> None:
    """
    Initialize SQLite database tables and indexes for users, RFID tokens, and attendance logs.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Student', 'Teacher', 'Admin', 'Lab-Instructor')),
                department TEXT NOT NULL DEFAULT 'Department of Electronics Engineering',
                campus TEXT NOT NULL DEFAULT 'MIT Campus, Anna University',
                rfid_uid TEXT UNIQUE,
                xp_points INTEGER NOT NULL DEFAULT 4850,
                streak_days INTEGER NOT NULL DEFAULT 14,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                rfid_uid TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Present' CHECK(status IN ('Present', 'Late', 'Lab-Verified', 'Flagged')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)

        # Module Lifecycle & Content Status Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_lifecycle (
                module_code TEXT PRIMARY KEY,
                module_title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Draft' CHECK(status IN ('Draft', 'AI-Generated', 'Human-Reviewed', 'Faculty-Approved', 'Published')),
                reviewer_name TEXT NOT NULL DEFAULT 'Faculty Review Board',
                reviewer_role TEXT NOT NULL DEFAULT 'Department Reviewer',
                completion_pct INTEGER NOT NULL DEFAULT 100,
                quality_score REAL NOT NULL DEFAULT 9.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT NOT NULL,
                previous_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                author TEXT NOT NULL,
                comment TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (module_code) REFERENCES module_lifecycle(module_code) ON DELETE CASCADE
            );
        """)

        # Performance Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_rfid ON users(rfid_uid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_id ON attendance(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_status ON module_lifecycle(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_changelog_module ON module_changelog(module_code);")

        conn.commit()


def register_user(
    user_id: str,
    name: str,
    email: str,
    password: str,
    role: str = "Student",
    department: str = "Department of Electronics Engineering",
    campus: str = "MIT Campus, Anna University",
    rfid_uid: Optional[str] = None,
    db_path: str = DB_FILE
) -> Dict[str, Any]:
    """
    Register a new user (Student or Teacher) into the VoltCore database with 260,000 iteration hashing.
    
    :return: Dictionary representation of the created user record (excluding password hash)
    :raises ValueError: On validation failure or duplicate record
    """
    clean_uid = user_id.strip()
    clean_name = name.strip()
    clean_email = email.strip().lower()
    clean_role = role.strip()

    if not clean_uid:
        raise ValueError("UserID cannot be empty.")
    if not clean_name:
        raise ValueError("Name cannot be empty.")
    if "@" not in clean_email or "." not in clean_email:
        raise ValueError(f"Invalid email address: '{email}'")
    if clean_role not in ('Student', 'Teacher', 'Admin', 'Lab-Instructor'):
        raise ValueError(f"Invalid role '{clean_role}'. Must be Student, Teacher, Admin, or Lab-Instructor.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long for university systems.")

    p_hash = hash_password(password)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (user_id, name, email, password_hash, role, department, campus, rfid_uid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (clean_uid, clean_name, clean_email, p_hash, clean_role, department, campus, rfid_uid))
            conn.commit()
        except sqlite3.IntegrityError as e:
            err_str = str(e)
            if "UNIQUE constraint failed: users.email" in err_str:
                raise ValueError(f"Email '{clean_email}' is already registered in VoltCore LMS.")
            elif "UNIQUE constraint failed: users.user_id" in err_str:
                raise ValueError(f"UserID '{clean_uid}' already exists.")
            elif "UNIQUE constraint failed: users.rfid_uid" in err_str:
                raise ValueError(f"RFID UID '{rfid_uid}' is already mapped to another student or faculty.")
            else:
                raise ValueError(f"Database Integrity Error: {e}")

    return {
        "user_id": clean_uid,
        "name": clean_name,
        "email": clean_email,
        "role": clean_role,
        "department": department,
        "campus": campus,
        "rfid_uid": rfid_uid,
        "status": "Registered Successfully"
    }


def verify_login(identifier: str, password: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by Email or UserID and plaintext password.
    
    :param identifier: UserID (e.g. '2023MITEC042') or registered Email
    :param password: Plaintext password to verify
    :return: Safe user profile dictionary if authenticated, or None if failed
    """
    clean_id = identifier.strip()

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, password_hash, role, department, campus, rfid_uid, xp_points, streak_days
            FROM users
            WHERE lower(email) = lower(?) OR lower(user_id) = lower(?);
        """, (clean_id, clean_id))
        row = cursor.fetchone()

        if not row:
            return None

        stored_hash = row["password_hash"]
        if verify_password(password, stored_hash):
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "role": row["role"],
                "department": row["department"],
                "campus": row["campus"],
                "rfid_uid": row["rfid_uid"],
                "xp_points": row["xp_points"],
                "streak_days": row["streak_days"],
                "authenticated": True
            }
        return None


def get_user_by_rfid(rfid_uid: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Lookup student or teacher by RFID UID token."""
    clean_rfid = rfid_uid.strip().upper()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, role, department, campus, rfid_uid, xp_points, streak_days
            FROM users
            WHERE upper(rfid_uid) = ?;
        """, (clean_rfid,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Lookup user by UserID."""
    clean_uid = user_id.strip()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, role, department, campus, rfid_uid, xp_points, streak_days
            FROM users
            WHERE lower(user_id) = lower(?);
        """, (clean_uid,))
        row = cursor.fetchone()
        return dict(row) if row else None


def record_attendance(
    user_id: str,
    node_id: str,
    rfid_uid: str,
    status: str = "Lab-Verified",
    db_path: str = DB_FILE
) -> Dict[str, Any]:
    """
    Log verified hardware attendance scan from ESP32 node.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance (user_id, node_id, rfid_uid, status)
            VALUES (?, ?, ?, ?);
        """, (user_id, node_id, rfid_uid, status))
        attendance_id = cursor.lastrowid
        
        # Award XP for active lab attendance
        cursor.execute("""
            UPDATE users SET xp_points = xp_points + 50 WHERE user_id = ?;
        """, (user_id,))
        conn.commit()

        cursor.execute("SELECT timestamp FROM attendance WHERE id = ?;", (attendance_id,))
        ts_row = cursor.fetchone()
        timestamp = ts_row["timestamp"] if ts_row else datetime.utcnow().isoformat()

    return {
        "attendance_id": attendance_id,
        "user_id": user_id,
        "node_id": node_id,
        "rfid_uid": rfid_uid,
        "status": status,
        "timestamp": timestamp,
        "xp_awarded": 50
    }


def get_attendance_history(user_id: Optional[str] = None, limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve chronologically ordered attendance logs with joined user details."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("""
                SELECT a.id, a.user_id, u.name, u.role, u.department, a.node_id, a.rfid_uid, a.status, a.timestamp
                FROM attendance a
                JOIN users u ON a.user_id = u.user_id
                WHERE lower(a.user_id) = lower(?)
                ORDER BY a.timestamp DESC
                LIMIT ?;
            """, (user_id.strip(), limit))
        else:
            cursor.execute("""
                SELECT a.id, a.user_id, u.name, u.role, u.department, a.node_id, a.rfid_uid, a.status, a.timestamp
                FROM attendance a
                JOIN users u ON a.user_id = u.user_id
                ORDER BY a.timestamp DESC
                LIMIT ?;
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]


VALID_LIFECYCLE_STATUSES = ('Draft', 'AI-Generated', 'Human-Reviewed', 'Faculty-Approved', 'Published')


def get_all_module_statuses(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve content lifecycle statuses for all curriculum modules."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT module_code, module_title, status, reviewer_name, reviewer_role, completion_pct, quality_score, last_updated
            FROM module_lifecycle
            ORDER BY module_code ASC;
        """)
        rows = cursor.fetchall()
        if not rows:
            seed_default_lifecycle_data(db_path)
            cursor.execute("""
                SELECT module_code, module_title, status, reviewer_name, reviewer_role, completion_pct, quality_score, last_updated
                FROM module_lifecycle
                ORDER BY module_code ASC;
            """)
            rows = cursor.fetchall()
        return [dict(r) for r in rows]


def update_module_lifecycle_status(
    module_code: str,
    new_status: str,
    author: str,
    comment: str = "",
    db_path: str = DB_FILE
) -> Dict[str, Any]:
    """Updates module status and records entry in module_changelog audit trail."""
    clean_code = module_code.strip().upper()
    if new_status not in VALID_LIFECYCLE_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of: {VALID_LIFECYCLE_STATUSES}")

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, module_title FROM module_lifecycle WHERE module_code = ?;", (clean_code,))
        row = cursor.fetchone()
        prev_status = row["status"] if row else "Draft"
        mod_title = row["module_title"] if row else clean_code

        cursor.execute("""
            INSERT INTO module_lifecycle (module_code, module_title, status, reviewer_name, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(module_code) DO UPDATE SET
                status = excluded.status,
                reviewer_name = excluded.reviewer_name,
                last_updated = CURRENT_TIMESTAMP;
        """, (clean_code, mod_title, new_status, author))

        cursor.execute("""
            INSERT INTO module_changelog (module_code, previous_status, new_status, author, comment)
            VALUES (?, ?, ?, ?, ?);
        """, (clean_code, prev_status, new_status, author, comment or f"Status transitioned to {new_status}"))

        conn.commit()
        return {
            "status": "success",
            "module_code": clean_code,
            "previous_status": prev_status,
            "new_status": new_status,
            "author": author,
            "comment": comment
        }


def get_module_changelog(module_code: Optional[str] = None, limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve module status changelog audit trail."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if module_code:
            cursor.execute("""
                SELECT id, module_code, previous_status, new_status, author, comment, timestamp
                FROM module_changelog
                WHERE module_code = ?
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (module_code.strip().upper(), limit))
        else:
            cursor.execute("""
                SELECT id, module_code, previous_status, new_status, author, comment, timestamp
                FROM module_changelog
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]


def seed_default_lifecycle_data(db_path: str = DB_FILE) -> None:
    """Seeds default lifecycle statuses for all 9 curriculum modules."""
    default_modules = [
        ("EC8701", "IoT Edge Node Foundations & Bare-Metal GPIO", "Published", "Dr. S. Ramanujam (MIT Faculty)", 100, 9.8),
        ("EC8702", "Embedded Systems Architecture & Microcontrollers", "Published", "Dr. P. V. Anand (MIT Faculty)", 100, 9.6),
        ("EC8703", "Defense UAV Telemetry & 2.4GHz FHSS", "Published", "Prof. K. Venkatesh (Aerospace Div)", 100, 9.9),
        ("EC8704", "Automotive Radar & Ultrasonic Edge Sensing", "Faculty-Approved", "Dr. M. Soundararajan", 95, 9.4),
        ("EC8705", "5-Stage RV32I RISC-V Soft-Core in Verilog", "Published", "Ashok Kumar A (Platform Architect)", 100, 10.0),
        ("EC8706", "FreeRTOS & Deterministic Multi-Core Scheduling", "Published", "Dr. S. Ramanujam", 100, 9.7),
        ("EC8707", "High-Speed Railway Edge AI Track Defect Vision", "Human-Reviewed", "Faculty Review Committee", 90, 9.1),
        ("EC8708", "ARM Cortex-M DMA Architecture & Zero-Copy IPC", "Published", "Ashok Kumar A (Platform Architect)", 100, 9.9),
        ("EC8709", "TinyML Edge AI Neural Networks & Vibration FFT", "Published", "Ashok Kumar A & MIT Faculty", 100, 9.9),
    ]

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for code, title, status, reviewer, comp, qscore in default_modules:
            cursor.execute("""
                INSERT OR IGNORE INTO module_lifecycle (module_code, module_title, status, reviewer_name, completion_pct, quality_score)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (code, title, status, reviewer, comp, qscore))
        conn.commit()


def seed_mit_campus_data(db_path: str = DB_FILE) -> None:
    """
    Seed initial Anna University / MIT Campus exemplar profiles.
    Includes student Ashok Kumar A and faculty mentors.
    """
    init_db(db_path)
    
    seeds = [
        {
            "user_id": "2023MITEC042",
            "name": "Ashok Kumar A",
            "email": "ashok.kumar.a@mitindia.edu",
            "password": "VoltCore@MIT2026!",
            "role": "Student",
            "department": "Department of Electronics Engineering",
            "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
            "rfid_uid": "E2 80 6F 3B"
        },
        {
            "user_id": "MIT-FAC-019",
            "name": "Dr. K. S. Parthasarathy",
            "email": "partha.ks@mitindia.edu",
            "password": "ApexFaculty#MIT2026",
            "role": "Teacher",
            "department": "Department of Electronics Engineering",
            "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
            "rfid_uid": "A4 12 99 F0"
        },
        {
            "user_id": "2023MITEC015",
            "name": "Kavitha Raman",
            "email": "kavitha.r@mitindia.edu",
            "password": "Embedded#IoT2026",
            "role": "Student",
            "department": "Department of Electronics Engineering",
            "campus": "Madras Institute of Technology (MIT) Campus, Anna University",
            "rfid_uid": "C3 4D 8A 11"
        }
    ]

    for user in seeds:
        try:
            register_user(
                user_id=user["user_id"],
                name=user["name"],
                email=user["email"],
                password=user["password"],
                role=user["role"],
                department=user["department"],
                campus=user["campus"],
                rfid_uid=user["rfid_uid"],
                db_path=db_path
            )
            print(f"[SEED] Created: {user['name']} ({user['user_id']}) - Role: {user['role']}")
        except ValueError as ex:
            if "already exists" in str(ex) or "already registered" in str(ex):
                pass
            else:
                print(f"[SEED NOTICE] {ex}")


if __name__ == "__main__":
    print("=" * 70)
    print(" VoltCore Apex Academia - LMS SQLite Backend Initialization")
    print(" Anna University / MIT Campus Standards | PBKDF2-HMAC-SHA256 (260,000 iters)")
    print("=" * 70)
    
    init_db()
    seed_mit_campus_data()

    # Self-test verification
    print("\n[VERIFICATION TEST]")
    test_user = verify_login("2023MITEC042", "VoltCore@MIT2026!")
    if test_user:
        print(f"SUCCESS: Logged in as '{test_user['name']}' ({test_user['role']})")
        print(f"  Department: {test_user['department']}")
        print(f"  Campus:     {test_user['campus']}")
        print(f"  RFID UID:   {test_user['rfid_uid']}")
        print(f"  XP Points:  {test_user['xp_points']} | Streak: {test_user['streak_days']} Days")
    else:
        print("ERROR: Test login failed.")
        sys.exit(1)
    
    # Hash format validation
    sample_hash = hash_password("DemoPassword123!")
    print(f"\nGenerated PBKDF2 Hash Structure:\n  {sample_hash[:45]}... [Length: {len(sample_hash)}]")
    assert verify_password("DemoPassword123!", sample_hash) is True
    assert verify_password("WrongPassword!", sample_hash) is False
    print("Cryptographic integrity check passed (Constant-time SHA256 verified).\n")

