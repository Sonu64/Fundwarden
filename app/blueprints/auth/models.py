from app.app import db # No more app.app as Our models folder is in same level as app folder

class User(db.Model):

    __tablename__ = "Users"
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    balance = db.Column(db.Integer, nullable = False)
    
    def __repr__(self):
        return f"Username: {self.username},  Password Hashed: {self.password},  Balance: Rs.{self.balance}. "
    
    def get_id(self):
        return self.id