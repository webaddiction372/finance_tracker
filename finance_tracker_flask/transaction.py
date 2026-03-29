from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user
from database import db
from models import Transaction
from datetime import datetime

def add_transaction_view():
    if request.method == 'POST':
        t_type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date'] or datetime.today().strftime('%Y-%m-%d')
        description = request.form['description']
        transaction = Transaction(user_id=current_user.id, type=t_type, amount=amount,
                                  category=category, date=date, description=description)
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html')
