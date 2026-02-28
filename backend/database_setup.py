import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# USERS TABLE (for login/register)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    fav_subject TEXT
)
""")

# STUDENT PROFILE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS profile (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    age INTEGER,
    gender TEXT,
    education TEXT,
    
    math_score REAL,
    science_score REAL,
    english_score REAL,
    overall_score REAL,

    skill_programming INTEGER,
    skill_creativity INTEGER,
    skill_communication INTEGER,
    skill_problem_solving INTEGER,
    skill_analytical INTEGER,

    interest TEXT,

    pers_extrovert INTEGER,
    pers_creative INTEGER,
    pers_leadership INTEGER,
    pers_risk INTEGER,

    apt_logical INTEGER,
    apt_verbal INTEGER,
    apt_numerical INTEGER,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

print("Database Tables Created Successfully!")

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN fav_subject TEXT")

conn.commit()
conn.close()
