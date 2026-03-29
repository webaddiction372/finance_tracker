from flask import request, flash, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import db
from flask_login import login_user

def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # hashed_password = generate_password_hash(password, method='sha256')
        from werkzeug.security import generate_password_hash, check_password_hash

# Use pbkdf2:sha256 (default recommended) 
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists.', 'danger')
    return render_template('register.html')

def login_user_view():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')
