import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tourist_secret_key_123_final'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///krishna.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='User')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    place_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    people = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()
    try:
        admin = User.query.filter_by(email="momsprince898@gmail.com").first()
        if not admin:
            admin = User(name="Admin", email="momsprince898@gmail.com", password=generate_password_hash("devil777"), role="Admin")
            db.session.add(admin)
            db.session.commit()
    except: db.session.rollback()

def get_place_image(place_name):
    # 1. WIKIPEDIA EXACT
    try:
        wiki_name = place_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and 'thumbnail' in res.json():
            return res.json()['thumbnail']['source']
    except: pass

    # 2. UNSPLASH FALLBACK - AB SAHI HAI
    clean_name = place_name.replace(" ", ",")  # <-- YE LINE SAHI KAR DI
    return f"https://source.unsplash.com/800x400/?{clean_name},tourism,landmark"

def get_google_map(place_name):
    return f"https://www.google.com/maps/search/?api=1&query={place_name.replace(' ', '+')}"

@app.route('/', methods=['GET', 'POST'])
def home():
    image = "https://source.unsplash.com/800x400/?Bhubaneswar,smart-city,building"
    place_name = None; map_link = None
    if request.method == 'POST':
        place_name = request.form.get('place_name')
        image = get_place_image(place_name)
        map_link = get_google_map(place_name)
    return render_template('index.html', image=image, place_name=place_name, map_link=map_link)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form['name']; email = request.form['email']
            password = generate_password_hash(request.form['password'])
            if User.query.filter_by(email=email).first(): flash("Email already exists!")
            else: db.session.add(User(name=name, email=email, password=password)); db.session.commit(); flash("Signup successful! Please Login"); return redirect(url_for('login'))
        except: db.session.rollback(); flash("Signup failed. Try again.")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']; password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id; session['role'] = user.role; session['name'] = user.name
                flash(f"Welcome {user.name}!")
                return redirect(url_for('admin_dashboard')) if user.role == 'Admin' else redirect(url_for('home'))
            else: flash("Invalid Email or Password")
        except: flash("Login error. Try again.")
    return render_template('login.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session: flash("Please login first"); return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            db.session.add(Booking(user_name=session['name'], user_email=User.query.get(session['user_id']).email, place_name=request.form['place'], date=request.form['date'], people=request.form['people']))
            db.session.commit(); flash(f"Slot booked successfully for {request.form['place']}!"); return redirect(url_for('home'))
        except: db.session.rollback(); flash("Booking failed.")
    place = request.args.get('place', '')
    return render_template('book.html', place=place)

@app.route('/admin')
def admin_dashboard():
    if session.get('role')!= 'Admin': flash("Admin access only"); return redirect(url_for('login'))
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    users = User.query.all()
    return render_template('admin.html', bookings=bookings, users=users)

@app.route('/logout')
def logout(): session.clear(); flash("Logged out successfully"); return redirect(url_for('home'))

if __name__ == '__main__': app.run(debug=False)