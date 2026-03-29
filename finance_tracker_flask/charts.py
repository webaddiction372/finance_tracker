import matplotlib.pyplot as plt
import io
import base64
from markupsafe import Markup
# from flask import Markup
from models import Transaction
from flask_login import current_user

def plot_expenses():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    categories = {}
    for t in transactions:
        if t.type == 'Expense':
            categories[t.category] = categories.get(t.category, 0) + t.amount
    if categories:
        plt.figure(figsize=(6,4))
        plt.bar(categories.keys(), categories.values(), color='#00a8ff')
        plt.xlabel('Category')
        plt.ylabel('Amount')
        plt.title('Expenses by Category')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return Markup(f'<img src="data:image/png;base64,{plot_url}">')
    else:
        return "No expense data to show."
