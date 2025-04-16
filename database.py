import sqlite3
import csv

def connect_db():
    return sqlite3.connect("student_performance.db")

def create_tables():
    conn = connect_db()
    c = conn.cursor()

    # Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            class TEXT,
            combination TEXT
        )
    ''')

    # Weekly marks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            week INTEGER,
            subject TEXT,
            score INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # Monthly summary table
    c.execute('''
        CREATE TABLE IF NOT EXISTS monthly_report (
            student_id TEXT PRIMARY KEY,
            average_score REAL,
            performance_category TEXT,
            recommendation TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # Weekly summary table
    c.execute('''
        CREATE TABLE IF NOT EXISTS weekly_report (
            student_id TEXT,
            week INTEGER,
            average_score REAL,
            performance_category TEXT,
            recommendation TEXT,
            PRIMARY KEY (student_id, week),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    conn.commit()
    conn.close()

def load_students_from_csv(csv_file):
    conn = connect_db()
    c = conn.cursor()
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            student_id, class_name, combination = row
            c.execute("INSERT OR IGNORE INTO students VALUES (?, ?, ?)", (student_id, class_name, combination))
    conn.commit()
    conn.close()

def add_student(student_id, class_name, combination):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO students (student_id, class, combination)
        VALUES (?, ?, ?)
    ''', (student_id, class_name, combination))
    conn.commit()
    conn.close()

def add_mark(student_id, week, subject, score):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO marks (student_id, week, subject, score)
        VALUES (?, ?, ?, ?)
    ''', (student_id, week, subject, score))
    conn.commit()
    conn.close()

def get_student_marks(student_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        SELECT week, subject, score FROM marks WHERE student_id = ?
    ''', (student_id,))
    records = c.fetchall()
    conn.close()
    return records

def get_weekly_marks(student_id, week):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        SELECT student_id, week, subject, score FROM marks
        WHERE student_id = ? AND week = ?
    ''', (student_id, week))
    records = c.fetchall()
    conn.close()
    return records

def save_monthly_report(student_id, average_score, performance_category, recommendation):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO monthly_report (student_id, average_score, performance_category, recommendation)
        VALUES (?, ?, ?, ?)
    ''', (student_id, average_score, performance_category, recommendation))
    conn.commit()
    conn.close()

def save_weekly_report(student_id, week, average_score, performance_category, recommendation):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO weekly_report (student_id, week, average_score, performance_category, recommendation)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_id, week, average_score, performance_category, recommendation))
    conn.commit()
    conn.close()

def get_all_monthly_reports():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT student_id, average_score, performance_category, recommendation FROM monthly_report')
    data = c.fetchall()
    conn.close()
    return data

def get_all_weekly_reports():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        SELECT student_id, week, average_score, performance_category, recommendation
        FROM weekly_report
        ORDER BY student_id, week
    ''')
    data = c.fetchall()
    conn.close()
    return data

