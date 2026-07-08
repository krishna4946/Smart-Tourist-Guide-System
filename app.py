import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tourist123' # signup ke liye zaroori

# Render pe Postgres use kar lena, local ke liye sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tourist.db'
db = SQLAlchemy(app)

# DB Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    place_name = db.Column(db.String(100))
    date = db.Column(db.String(20))
    slots = db.Column(db.Integer)

with app.app_context():
    db.create_all()

def get_unsplash_image(place_name):
    access_key = os.environ.get('UNSPLASH_KEY')
    if not access_key:
        return "https://via.placeholder.com/600x400?text=No+Image"
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"{place_name} Odisha India",
            "client_id": access_key,
            "per_page": 1,
            "orientation": "landscape"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
    except:
        pass
    return "https://via.placeholder.com/600x400?text=No+Image"

@app.route('/', methods=['GET', 'POST'])
def home():
    image = None
    place_name = None
    
    if request.method == 'POST':
        place_name = request.form.get('place_name')
        # Ab DB check nahi karega - seedha Unsplash se lega
        image = get_unsplash_image(place_name)
    
    return render_template('index.html', image=image, place_name=place_name)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Now book your slot")
        return redirect(url_for('book'))
    return render_template('signup.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        booking = Booking(
            user_email=request.form['email'],
            place_name=request.form['place'],
            date=request.form['date'],
            slots=request.form['slots']
        )
        db.session.add(booking)
        db.session.commit()
        flash("Slot booked successfully!")
        return redirect(url_for('home'))
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)