import sqlite3
from contextlib import contextmanager
import streamlit as st # type: ignore # Import st for displaying info in setup_database

DB_NAME = 'student_portal.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Students table - now includes username, password, and photo for ID card
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL, -- Ensure roll numbers are unique
                class TEXT NOT NULL,
                slot TEXT NOT NULL,
                photo BLOB -- Stores image as binary data
            )
        ''')
        # Teachers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slot TEXT UNIQUE NOT NULL -- Each slot has one teacher
            )
        ''')
        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Results table (student course results - NO marks, as per your last DB)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY(course_id) REFERENCES courses(id),
                UNIQUE(student_id, course_id) -- Prevent duplicate results for same student-course
            )
        ''')
        # Attendance table (date, status as per your last DB)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id),
                UNIQUE(student_id, date) -- One attendance record per student per day
            )
        ''')
        self.conn.commit()

    def close(self):
        self.conn.close()

# Global instance to ensure single DB connection
_db_instance = None

def setup_database():
    """Initializes the database and creates tables if they don't exist."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        # Insert default student user if not exists
        with get_db_connection() as cursor:
            cursor.execute("SELECT id FROM students WHERE username = ?", ('student',))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO students (username, password, name, roll_number, class, slot, photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               ('student', 'student123', 'Default Student User', 'GIAIC-DSU-001', 'Batch 2024', 'Monday 2-5 PM', None))
                st.info("Default student account 'student'/'student123' created for testing.")
            
            # Insert default courses (if not exists)
            cursor.execute("INSERT OR IGNORE INTO courses (name) VALUES ('Typescript')")
            cursor.execute("INSERT OR IGNORE INTO courses (name) VALUES ('Next.js')")
            cursor.execute("INSERT OR IGNORE INTO courses (name) VALUES ('Python')")
            cursor.execute("INSERT OR IGNORE INTO courses (name) VALUES ('Agentic AI')")

            # Insert default teachers with unique slots (if not exists)
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Zia', 'Monday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Asharib', 'Tuesday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Ali Aftab', 'Wednesday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Aneeq', 'Thursday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Hamzah Syed', 'Friday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Ali Aftab', 'Saturday 2-5 PM')")
            cursor.execute("INSERT OR IGNORE INTO teachers (name, slot) VALUES ('Sir Muhammad Bilal Khan', 'Sunday 2-5 PM')")


@contextmanager
def get_db_connection():
    """Provides a database connection and cursor, handling commit/rollback."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()