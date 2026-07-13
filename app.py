from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import random
import os

app = Flask(__name__)
app.secret_key = 'travelista_secret_key_123' 

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'momsprince898@gmail.com' # Tera gmail
app.config['MAIL_PASSWORD'] = 'qudq tumi jgmd drf' .

mail = Mail(app)

# Temporary storage for OTP - production me database use karna
otp_storage = {}

# ===== HOME ROUTE =====
@app.route('/')
def home():
    return render_template('index.html')

# ===== FORGOT PASSWORD ROUTE =====
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # OTP Generate karo 6 digit
        otp = random.randint(100000, 999999)
        otp_storage[email] = str(otp)

        try:
            # Mail bhejo
            msg = Message('Travelista - Password Reset OTP',
                          sender='momsprince898@gmail.com',
                          recipients=[email])
            msg.body = f"""Hi,

Your OTP for password reset is: {otp}

This OTP is valid for 10 minutes.
Do not share this OTP with anyone.

- Team Travelista"""

            mail.send(msg)
            flash('OTP sent to your email!', 'success')
            session['reset_email'] = email
            return redirect(url_for('verify_otp'))

        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')
            print("Mail Error:", e)

    return render_template('forgot_pass.html')

# ===== VERIFY OTP ROUTE =====
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        user_otp = request.form['otp']
        email = session['reset_email']

        if email in otp_storage and otp_storage[email] == user_otp:
            flash('OTP Verified! Now set new password', 'success')
            del otp_storage[email] # OTP delete kar do
            session.pop('reset_email', None)
            return redirect(url_for('reset_password'))
        else:
            flash('Invalid OTP. Try again.', 'danger')

    return render_template('verify_otp.html')

# ===== RESET PASSWORD ROUTE =====
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['password']
        flash('Password reset successful!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_pass.html')

# ===== LOGIN ROUTE DUMMY =====
@app.route('/login')
def login():
    return "Login Page"

if __name__ == '__main__':
    app.run(debug=True)