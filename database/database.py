
from pathlib import Path
import sqlite3


# ---------------------------------------------------------
# DATABASE PATH
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATABASE_NAME = BASE_DIR / "student_career.db"


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)

    # Allows us to access columns by name
    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ---------------------------------------------------------
# CREATE ALL TABLES
# ---------------------------------------------------------

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    """)

    # -----------------------------------------------------
    # STUDENT PROFILE TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            phone TEXT,
            college TEXT,
            degree TEXT,
            branch TEXT,
            cgpa REAL,
            graduation_year INTEGER,
            skills TEXT,
            projects TEXT,
            interest TEXT,
            preferred_career TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # RESUMES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            resume_text TEXT,
            detected_skills TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # SKILL GAP ANALYSIS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gap_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            career TEXT NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            match_percentage REAL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # CAREER RECOMMENDATIONS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            career TEXT NOT NULL,
            match_score REAL,
            matched_skills TEXT,
            matched_interests TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # JOB RECOMMENDATIONS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            job_type TEXT,
            career TEXT,
            match_score REAL,
            matched_skills TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # APPLICATION TRACKER TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            job_type TEXT,
            application_date TEXT,
            status TEXT DEFAULT 'Applied',
            notes TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    # -----------------------------------------------------
    # MIGRATION FOR OLD STUDENT PROFILE TABLE
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(student_profiles)")

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    required_columns = {
        "phone": "TEXT",
        "college": "TEXT",
        "degree": "TEXT",
        "branch": "TEXT",
        "cgpa": "REAL",
        "graduation_year": "INTEGER",
        "skills": "TEXT",
        "projects": "TEXT",
        "interest": "TEXT",
        "preferred_career": "TEXT",
    }

    # Add missing columns
    for column, column_type in required_columns.items():

        if column not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE student_profiles
                ADD COLUMN {column} {column_type}
                """
            )

    # -----------------------------------------------------
    # MIGRATE OLD COLUMN NAMES IF THEY EXIST
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(student_profiles)")

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    # Old column: interests
    # New column: interest
    if "interests" in existing_columns:

        cursor.execute("""
            UPDATE student_profiles
            SET interest = interests
            WHERE
                (interest IS NULL OR interest = '')
                AND interests IS NOT NULL
        """)

    # Old column: prefered_career
    # New column: preferred_career
    if "prefered_career" in existing_columns:

        cursor.execute("""
            UPDATE student_profiles
            SET preferred_career = prefered_career
            WHERE
                (preferred_career IS NULL OR preferred_career = '')
                AND prefered_career IS NOT NULL
        """)

    # -----------------------------------------------------
    # SAVE CHANGES
    # -----------------------------------------------------

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# RUN DIRECTLY
# ---------------------------------------------------------

if __name__ == "__main__":

    create_tables()

    print("======================================")
    print(" Database created successfully!")
    print(" All project tables are ready.")
    print("======================================")

