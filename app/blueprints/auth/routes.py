from flask import Blueprint, render_template, Flask, request as req, redirect, url_for
from flask import jsonify
#Import DB and DB Models
from app.app import db, bcrypt
from app.blueprints.auth.models import User

auth  = Blueprint('auth', __name__)

@auth.route("/")
def index():
    return render_template('auth/index.html')

# url_for('auth.login') ---> Points to the login route handler of the core BP. Because you don't have any @core.route decorators in models.py, Flask never associates anything in models.py with the "core" endpoint.

# When you use Blueprints, Flask "prefixes" every function name with the name of the Blueprint. This is to prevent naming collisions (e.g., if you have an index route in auth and an index route in main). So though login and register handlers of auth are in same file /auth/routes.py, while using url_for() we have to use auth.login, auth.register and auth.index
#
@auth.route("/login", methods = ['GET', 'POST'])
def login():
    if req.method == 'GET':
        return render_template('auth/login.html')
    elif req.method == 'POST':
        data = req.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Get Row for the Username
        userRow = User.query.filter(User.username == username).first()
        # User doesn't exist
        if not userRow:
            return jsonify({'error': "Username not Found !"}), 401
        
        hashedPassword = userRow.password;
        # Check hashed password
        passwordMatched = bcrypt.check_password_hash(hashedPassword, password)
        # Password doesn't match
        if not passwordMatched:
            return jsonify({'error': "Wrong Password !"}), 401
        
        else:
            return jsonify({
                'message': "Login Successful !",
                'redirect': url_for('auth.index')
            }), 200
        
    else:
        return "Invalid Request !"
    

# url_for('core.register') ---> Points to the register route handler of the Core BP. 
@auth.route("/register", methods = ['GET', 'POST'])
def register():
    if req.method == 'GET':
        return render_template('auth/register.html')
    elif req.method == 'POST':
        data = req.get_json()
        username = data['username']
        
        #Checking for Uniqueness of the Username
        existingUser = User.query.filter(User.username == username).first()
        
        if existingUser:
            return jsonify({'error': "Username Already Exists !!"}), 409
        
        password = data['password']
        # Hashing Password
        hashedPassword = bcrypt.generate_password_hash(password)
        
        userObject = User(username = username, password = hashedPassword, balance = 1000)
        db.session.add(userObject)
        db.session.commit()
        return jsonify({
            'message': "Registration Successful !",
            'redirect': url_for('auth.login')
        }), 200
    else:
        return "Invalid Request !"