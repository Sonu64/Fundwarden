from flask import Blueprint, render_template, Flask, request as req

#Import DB Models
from app.blueprints.auth.models import User

auth  = Blueprint('auth', __name__)

@auth.route("/")
def index():
    return render_template('auth/index.html')

# url_for('core.login') ---> Points to the login route handler of the core BP. Because you don't have any @core.route decorators in models.py, Flask never associates anything in models.py with the "core" endpoint.
@auth.route("/login", methods = ['GET', 'POST'])

def login():
    if req.method == 'GET':
        return render_template('auth/login.html')
    elif req.method == 'POST':
        return "Post Request to Login";
    else:
        return "Invalid Request !"
    

# url_for('core.register') ---> Points to the register route handler of the Core BP. 
@auth.route("/register", methods = ['GET', 'POST'])
def register():
    if req.method == 'GET':
        return render_template('auth/register.html')
    elif req.method == 'POST':
        return "Post request to Register"
    else:
        return "Invalid Request !"