from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=True)
    user_type = db.Column(db.String(50), nullable=True)
    # reviews = db.relationship('Review', backref='user', lazy='dynamic')
    # vendors = db.relationship('Vendor', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='vendor', lazy='dynamic')
    # markets = db.relationship('Market', secondary=vendor_markets, back_populates="vendors")

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    availability = db.Column(db.Boolean, default=True)
    contact_email = db.Column(db.String(120))  
    contact_phone = db.Column(db.String(20))  
