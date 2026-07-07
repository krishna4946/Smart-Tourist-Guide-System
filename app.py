from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'krishna_secret_key_2026'

DB_FILE = "krishna.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, email TEXT UNIQUE,
         phone TEXT, password TEXT, role TEXT DEFAULT 'User')""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS places
        (id INTEGER PRIMARY KEY AUTOINCREMENT, place_name TEXT, location TEXT,
         category TEXT, contact TEXT, visit_date TEXT, start_time TEXT, end_time TEXT,
         features TEXT, added_by INTEGER, added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
         status TEXT DEFAULT 'Pending')""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_selections
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, place_id INTEGER,
         selected_on DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute("SELECT id FROM users WHERE email=?", ("momsprince898@gmail.com",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (full_name, email, phone, password, role) VALUES (?,?,?,?,?)",
                       ("Admin", "momsprince898@gmail.com", "8984166820", hash_password("krish8984na"), "Admin"))

    cursor.execute("SELECT COUNT(*) FROM places")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM users WHERE email=?", ("momsprince898@gmail.com",))
        admin_id = cursor.fetchone()[0]
        places = [
            ('Jagannath Temple', 'Puri, Odisha', 'Temple', '06752-222002', '2026-01-01', '05:00 AM', '09:00 PM', 'Famous temple, Sea beach', admin_id, 'Approved'),
            ('Konark Sun Temple', 'Konark, Odisha', 'Monument', '06758-236821', '2026-01-01', '06:00 AM', '06:00 PM', 'UNESCO World Heritage', admin_id, 'Approved'),
            ('Nandankanan Zoo', 'Bhubaneswar, Odisha', 'Zoo', '0674-2547857', '2026-01-01', '08:00 AM', '05:00 PM', 'White Tigers, Safari', admin_id, 'Approved'),
            ('Chilika Lake', 'Puri, Odisha', 'Nature', '06756-222001', '2026-01-01', '06:00 AM', '06:00 PM', 'Migratory birds, Dolphins', admin_id, 'Approved')
        ]
        cursor.executemany("INSERT INTO places (place_name, location, category, contact, visit_date, start_time, end_time, features, added_by, status) VALUES (?,?,?,?,?,?,?,?,?,?)", places)

    conn.commit()
    conn.close()

@app.route('/')
def welcome():
    return render_template('index.html', page='welcome')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        if not email or not password:
            flash('Enter Email and Password!', 'error')
            return redirect(url_for('login'))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, role FROM users WHERE email=? AND password=?",
                      (email, hash_password(password)))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[2]
            session['email'] = email
            flash(f'Welcome {user[1]}!', 'success')
            if user[2] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid Email or Password', 'error')

    return render_template('index.html', page='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        password = request.form['password'].strip()

        if not all([name, email, phone, password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('signup'))
        if not phone.isdigit() or len(phone)!= 10:
            flash('Contact Number must be 10 digits', 'error')
            return redirect(url_for('signup'))
        if "@" not in email or "." not in email:
            flash('Please enter a valid Email', 'error')
            return redirect(url_for('signup'))
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('signup'))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            flash('Email already exists!', 'error')
            conn.close()
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (full_name, email, phone, password, role) VALUES (?,?,?,?,?)",
                      (name, email, phone, hash_password(password), "User"))
        conn.commit()
        conn.close()
        flash('Registration Successful! Please Login', 'success')
        return redirect(url_for('login'))

    return render_template('index.html', page='signup')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role']!= 'User':
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    category = request.args.get('category', 'All')

    sql = "SELECT id, place_name, location, category, contact, visit_date, start_time, end_time, features FROM places WHERE status='Approved'"
    params = []
    if query:
        sql += " AND place_name LIKE?"
        params.append(f"%{query}%")
    if location:
        sql += " AND location LIKE?"
        params.append(f"%{location}%")
    if category!= "All":
        sql += " AND category =?"
        params.append(category)

    cursor.execute(sql, params)
    places = cursor.fetchall()
    conn.close()

    return render_template('index.html', page='user_dashboard', places=places, user_name=session['user_name'])

@app.route('/add_place', methods=['POST'])
def add_place():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data = {k: request.form[k].strip() for k in ['place_name', 'location', 'category', 'contact', 'visit_date', 'start_time', 'end_time', 'features']}
    if not all(data.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('user_dashboard'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO places (place_name, location, category, contact, visit_date,
                    start_time, end_time, features, added_by, status) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                   (data['place_name'], data['location'], data['category'], data['contact'], data['visit_date'],
                    data['start_time'], data['end_time'], data['features'], session['user_id'], 'Pending'))
    conn.commit()
    conn.close()
    flash('Place submitted! Status: Pending. Wait for admin approval.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/select_place/<int:place_id>')
def select_place(place_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_selections WHERE user_id=? AND place_id=?", (session['user_id'], place_id))
    if cursor.fetchone():
        flash('Already added to your list!', 'info')
    else:
        cursor.execute("INSERT INTO user_selections (user_id, place_id) VALUES (?,?)", (session['user_id'], place_id))
        conn.commit()
        flash('Added to your list!', 'success')
    conn.close()
    return redirect(url_for('user_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role']!= 'Admin':
        return redirect(url_for('login'))

    status = request.args.get('status', 'All')
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT id, place_name, location, category, contact, visit_date, start_time, end_time, features, status FROM places"
    params = []
    if status!= "All":
        sql += " WHERE status=?"
        params.append(status)
    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    places = cursor.fetchall()

    cursor.execute("SELECT id, full_name, email, phone, role FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()

    return render_template('index.html', page='admin_dashboard', places=places, users=users, admin_name=session['user_name'])

@app.route('/approve_place/<int:place_id>')
def approve_place(place_id):
    if 'user_id' not in session or session['role']!= 'Admin':
        return redirect(url_for('login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE places SET status='Approved' WHERE id=?", (place_id,))
    conn.commit()
    conn.close()
    flash('Place approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_place/<int:place_id>')
def delete_place(place_id):
    if 'user_id' not in session or session['role']!= 'Admin':
        return redirect(url_for('login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM places WHERE id=?", (place_id,))
    conn.commit()
    conn.close()
    flash('Place deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)