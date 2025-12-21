from app.app import db
from flask_login import UserMixin # 1. Import UserMixin

class User(db.Model, UserMixin):

    __tablename__ = "Users"
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    balance = db.Column(db.Integer, nullable = False)
    
    def __repr__(self):
        return f"Username: {self.name},  Password Hashed: {self.password},  Balance: Rs.{self.balance}. "
    
    def get_id(self):
        return self.id