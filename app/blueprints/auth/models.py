from flask import current_app # To Successfully import the current app instance before it has been created in the factory function create_app(). It will cause error for [from app.app import app], because app is initialized only inside the facotry function and the import triggers at the very beginning, when app instance is not yet created in app.app
from flask_login import UserMixin # 1. Import UserMixin
from itsdangerous import URLSafeTimedSerializer
from app.app import db

class User(db.Model, UserMixin):

    __tablename__ = "Users"
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    balance = db.Column(db.Integer, nullable = False)
    
    
    # This is not a static method, because it needs access to self, which is given by parameter self.
    # We have to use this method on a user filtered from the DB using User.query.filter().first()
    def generateResetToken(self):
        # Create URLSafeTimedSerializer Object, with seccret key as our apps secret key
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        # .dumps() will generate a Serialized String (a String of random chars) for the provided value (Here E-Mail) using the secret key it was initialized with, the current TimeStamp and the Salt.
        # Signature = hashing_algorithm(Data, Secret_key, salt)
        # Token = <E-Mail random string>.<Timestamp random string>.<Signature>
        # Random strings for E-Mail and Timestamp are generated using Normal Base64 encoder, no need of secret key or salt
        return s.dumps(self.email, salt = "Password_Reset_Salt")
    
    
    @staticmethod # Can be called even if user is not logged in, It does not need access to self, It just loads the 
    # String values from a encoded Serializer. So call it as User.verifyResetToken(), no need to query the user based on email before this. !!!!!!!!! Static methods must not have self as a Parameter !!!!!!!!!!!!
    def verifyResetToken(token, expirationTime = 300):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt = "Password_Reset_Salt", max_age = expirationTime)
            return email
        except Exception as e:
            print(e)
            return None
            
    
    
    def __repr__(self):
        return f"Username: {self.name},  Password Hashed: {self.password},  Balance: Rs.{self.balance}. "
    
    def get_id(self):
        return self.id