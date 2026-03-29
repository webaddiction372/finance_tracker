from database import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    transactions = db.relationship('Transaction', backref='owner')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    date = db.Column(db.String(50))
    description = db.Column(db.String(200))
