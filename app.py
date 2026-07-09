import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tourist_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///krishna.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default='User')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    place_name = db.Column(db.String(200))
    date = db.Column(db.String(20))
    people = db.Column(db.Integer)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="momsprince898@gmail.com").first():
        admin = User(name="Admin", email="momsprince898@gmail.com", password=generate_password_hash("devil777"), role="Admin")
        db.session.add(admin)
        db.session.commit()

# UNSPLASH HATA DIYA. AB WIKIPEDIA SE IMAGE AAYEGI
def get_place_image(place_name):
    try:
        # Wikipedia se direct image uthayega
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{place_name}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if 'thumbnail' in data:
                return data['thumbnail']['source']
    except: pass
    
    # Agar wikipedia pe na mile to default Bhubaneswar
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Lingaraj_Temple_Bhubaneswar.jpg/800px-Lingaraj_Temple_Bhubaneswar.jpg"

def get_google_map(place_name):
    query = place_name.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

@app.route('/', methods=['GET', 'POST'])
def home():
    image = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Lingaraj_Temple_Bhubaneswar.jpg/800px-Lingaraj_Temple_Bhubaneswar.jpg" # Default Logo
    place_name = None
    map_link = None
    if request.method == 'POST':
        place_name = request.form.get('place_name')
        image = get_place_image(place_name) # NAYA FUNCTION
        map_link = get_google_map(place_name)
    return render_template('index.html', image=image, place_name=place_name, map_link=map_link)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']; email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first(): flash("Email already exists!")
        else: db.session.add(User(name=name, email=email, password=password)); db.session.commit(); flash("Signup successful!"); return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']; password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id; session['role'] = user.role; session['name'] = user.name
            return redirect(url_for('admin_dashboard')) if user.role == 'Admin' else redirect(url_for('home'))
        else: flash("Invalid Email or Password")
    return render_template('login.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session: flash("Please login first"); return redirect(url_for('login'))
    if request.method == 'POST':
        db.session.add(Booking(user_name=session['name'], user_email=User.query.get(session['user_id']).email, place_name=request.form['place'], date=request.form['date'], people=request.form['people']))
        db.session.commit(); flash(f"Slot booked for {request.form['place']}!"); return redirect(url_for('home'))
    place = request.args.get('place', '')
    return render_template('book.html', place=place)

@app.route('/admin')
def admin_dashboard():
    if session.get('role')!= 'Admin': flash("Admin access only"); return redirect(url_for('login'))
    return render_template('admin.html', bookings=Booking.query.all(), users=User.query.all())

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))

if __name__ == '__main__': app.run(debug=True)