from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -------------------
# Models
# -------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # Income or Expense
    amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# -------------------
# User loader
# -------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------
# Routes
# -------------------
@app.route('/')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    income = sum(t.amount for t in transactions if t.type=='Income')
    expense = sum(t.amount for t in transactions if t.type=='Expense')
    balance = income - expense

    # Prepare data for Chart.js
    chart_labels = [t.category for t in transactions if t.type=='Expense']
    chart_values = [t.amount for t in transactions if t.type=='Expense']

    return render_template('dashboard.html',
                           transactions=transactions,
                           income=income,
                           expense=expense,
                           balance=balance,
                           chart_labels=chart_labels,
                           chart_values=chart_values)

# -------------------
# Registration
# -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# -------------------
# Login
# -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
    return render_template('login.html')

# -------------------
# Logout
# -------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------
# Add Transaction
# -------------------
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        t_type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        description = request.form['description']
        transaction = Transaction(type=t_type, amount=amount, category=category,
                                  date=date, description=description, user_id=current_user.id)
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction added!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html')

# -------------------
# Edit Transaction
# -------------------
@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        transaction.type = request.form['type']
        transaction.amount = float(request.form['amount'])
        transaction.category = request.form['category']
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        transaction.description = request.form['description']
        db.session.commit()
        flash("Transaction updated!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_transaction.html', transaction=transaction)

# -------------------
# Delete Transaction
# -------------------
@app.route('/delete/<int:transaction_id>', methods=['POST','GET'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction deleted!", "success")
    return redirect(url_for('dashboard'))

# -------------------
# Run App
# -------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
