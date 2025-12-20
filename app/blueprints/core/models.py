from app.app import db
from app.blueprints.auth.models import User


class Categories(db.Model):
    __tablename__ = "Categories"
    
    id = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer, db.ForeignKey(User.id), nullable = False)
    name = db.Column(db.String, nullable = False)
    budget = db.Column(db.Integer, nullable = False)
    spent = db.Column(db.Integer, nullable = False)
    remaining = db.Column(db.Integer, nullable = False)
    
    def __repr__(self):
        return f"Category Name: {self.name}, Associated UserID: {self.userID}, Budget Allocated: Rs.{self.budget}, Spent Amount: {self.spent}, Remaining amount: {self.remaining}."
    
    def getCategoryID(self):
        return self.id
        