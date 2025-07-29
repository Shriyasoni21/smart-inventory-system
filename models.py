# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # Relationships to easily access a user's items and sales
    inventory_items = db.relationship('InventoryItem', backref='owner', lazy=True)
    sales = db.relationship('Sale', backref='seller', lazy=True)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=5)
    # START: NEW USER_ID FOREIGN KEY
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # END: NEW USER_ID FOREIGN KEY

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)
    # START: NEW USER_ID FOREIGN KEY
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # END: NEW USER_ID FOREIGN KEY