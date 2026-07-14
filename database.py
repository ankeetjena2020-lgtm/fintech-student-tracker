import sqlite3

DB_NAME = "student_savings.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 2. Goals Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            target_date TEXT NOT NULL,
            current_savings REAL DEFAULT 0
        )
    ''')
    
    # 3. Expenses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    # 4. Investments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            shares TEXT NOT NULL,
            buy_price TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    # 5. PHASE 7: Bill Split Table (Group Expenses Log)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            total_amount REAL NOT NULL,
            paid_by TEXT NOT NULL,
            friends TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# ================= AUTH FUNCTIONS =================

def register_user(username, password_hash):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# ================= CORE APP FUNCTIONS =================

def add_goal(user_id, name, target_amount, target_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO goals (user_id, name, target_amount, target_date) VALUES (?, ?, ?, ?)", (user_id, name, target_amount, target_date))
    conn.commit()
    conn.close()

def get_goals(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, target_amount, target_date, current_savings FROM goals WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_goal(goal_id, name, target_amount, target_date, current_savings):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE goals SET name = ?, target_amount = ?, target_date = ?, current_savings = ? WHERE id = ?', (name, target_amount, target_date, current_savings, goal_id))
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()

def add_expense(user_id, category, amount, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)", (user_id, category, amount, date))
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount, date FROM expenses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def add_investment(user_id, ticker, shares, buy_price, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO investments (user_id, ticker, shares, buy_price, date) VALUES (?, ?, ?, ?, ?)", (user_id, str(ticker).upper().strip(), str(shares), str(buy_price), str(date)))
    conn.commit()
    conn.close()

def get_investments(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker, shares, buy_price, date FROM investments WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_investment(inv_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investments WHERE id = ?", (inv_id,))
    conn.commit()
    conn.close()

# ================= PHASE 7: BILL SPLITTER FUNCTIONS =================

def add_bill(user_id, description, total_amount, paid_by, friends, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bills (user_id, description, total_amount, paid_by, friends, date) VALUES (?, ?, ?, ?, ?, ?)", 
                   (user_id, description, total_amount, paid_by, friends, date))
    conn.commit()
    conn.close()

def get_bills(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, total_amount, paid_by, friends, date FROM bills WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_bill(bill_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()