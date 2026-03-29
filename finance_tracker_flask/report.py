from flask_login import current_user
from models import Transaction

def get_balance():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    income = sum(t.amount for t in transactions if t.type == 'Income')
    expense = sum(t.amount for t in transactions if t.type == 'Expense')
    balance = income - expense
    return income, expense, balance
