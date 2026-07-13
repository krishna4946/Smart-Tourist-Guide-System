from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # change this

# ===== EMAIL CONFIG =====
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com' # apna gmail daal
app.config['MAIL_PASSWORD'] = 'your_app_password' # 16 digit app password daal
mail = Mail(app)

# Temporary storage for OTP
otp_storage = {}

# ===== HOME PAGE =====
@app.route('/')
def index():
    return render_template('index.html') # yahi pe login + signup dono hai

# ===== LOGIN =====
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Yaha DB check karna hai
    # if email == "test@gmail.com" and password == "123":
    # session['user'] = email
    # return redirect('/dashboard')

    flash('Login successful!')
    return redirect('/book') # login ke baad kaha bhejna hai

# ===== SIGNUP =====
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Yaha DB me save karna hai
    # save_user(name, email, password)

    flash('Signup successful! Now login.')
    return redirect('/') # wapas home page pe

# ===== FORGOT PASSWORD =====
@app.route('/forget_pass')
def forget_pass():
    return render_template('forget_pass.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    otp = random.randint(100000, 999999)
    otp_storage[email] = otp

    msg = Message('Your OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP is {otp}'
    mail.send(msg)

    return render_template('verify_otp.html', email=email)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    otp = int(request.form['otp'])

    if otp_storage.get(email) == otp:
        return render_template('reset_pass.html', email=email)
    else:
        flash('Invalid OTP')
        return redirect('/forget_pass')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_pass = request.form['password']

    # Yaha DB me password update karo
    flash('Password reset successful')
    return redirect('/')

# ===== OTHER PAGES =====
@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)