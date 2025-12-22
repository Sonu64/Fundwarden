from flask import Blueprint, render_template, Flask, request as req, redirect, url_for, flash
from flask import jsonify
#Import DB and DB Models
from app.app import db, bcrypt, mail
from app.blueprints.auth.models import User
# Import Authentication modules from flask_login
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message

auth  = Blueprint('auth', __name__)

@auth.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('core.index')) # Dashboard
    else:
        return render_template('/auth/index.html') # Landing page
# url_for('auth.login') ---> Points to the login route handler of the core BP. Because you don't have any @core.route decorators in models.py, Flask never associates anything in models.py with the "core" endpoint.

# When you use Blueprints, Flask "prefixes" every function name with the name of the Blueprint. This is to prevent naming collisions (e.g., if you have an index route in auth and an index route in main). So though login and register handlers of auth are in same file /auth/routes.py, while using url_for() we have to use auth.login, auth.register and auth.index
#
@auth.route("/login", methods = ['GET', 'POST'])
def login():
    if req.method == 'GET':
        return render_template('auth/login.html')
    elif req.method == 'POST':
        data = req.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        # Get Row for the Username
        userRow = User.query.filter(User.email == email).first()
        # User doesn't exist
        if not userRow:
            return jsonify({'error': "E-Mail doesn't exist !"}), 401
        
        hashedPassword = userRow.password
        # Check hashed password
        passwordMatched = bcrypt.check_password_hash(hashedPassword, password)
        # Password doesn't match
        if not passwordMatched:
            return jsonify({'error': "Wrong Password !"}), 401
        
        else:
            login_user(userRow) # Cookie with userID: <userID> saved but will not persist to subsequent requests if LoginManager.user_loader is not properly configured.
            # login_user() finds the ID with the .get_id attribute provided by UserMixin
            # 
            return jsonify({
                'message': "Login Successful !",
                'redirect': url_for('core.index') # Dashboard on successful Login
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
        email = data['email']
        
        #Checking for Uniqueness of the Username
        existingUser = User.query.filter(User.email == email).first()
        
        if existingUser:
            return jsonify({'error': "An account with that E-Mail Already Exists !!"}), 409
        
        name = data['name']
        password = data['password']
        # Hashing Password
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        
        userObject = User(email = email, name = name, password = hashedPassword, balance = 1000)
        db.session.add(userObject)
        db.session.commit()
        
        return jsonify({
            'message': "Registration Successful !",
            'redirect': url_for('auth.login')
        }), 200
        
    else:
        return "Invalid Request !"
    

@auth.route("logout")
def logout():
    logout_user()
    return redirect(url_for('auth.index')) # Landing Page


@auth.route("forgotPassword", methods = ['GET', 'POST'])
def forgotPassword():
    if req.method == 'GET':
        return render_template('auth/forgot.html')
    elif req.method == 'POST':
        email = req.form.get("email")
        user = User.query.filter(User.email == email).first()
        if not user:
            return "User Not Found !", 409
        try:
            # Generate Reset Token, from user specific generateResetToken() function, which gets access to current user's email via self.email. But if we had made it a static method, we had to pass queried user from here. But being a normal method, it gets to user via self.
            token = user.generateResetToken() 
            resetLink = url_for('auth.resetPassword', token = token, _external = True)
            # Send Reset Link via E-Mail
            msg = Message("Password Reset Request", sender = "sonusantu64@gmail.com", recipients = [email])
            msg.body = f"Fundwarden Password Reset Link: {resetLink}"
            mail.send(msg)
            flash("Password Reset Link sent in E-Mail, please check your Inbox.")
            print("Mail Sent !")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            flash("Error Occured while Sending E-Mail !")
            return "An Error occured while sending Password reset E-Mail !"
    else:
        return "Invalid Request !"
    

# Use the Token as an URL Parameter to generate different reset links for different users
@auth.route("resetPassword/<token>", methods = ['GET', 'POST'])
def resetPassword(token):
    email = User.verifyResetToken(token) # Decode the E-Mail part from the token
    if not email:
        return "Invalid E-Mail Address or Token Expired !"
    
    if req.method == 'GET':
        # A Valid GET request, matching the URL syntax can only be sent by clicking on the Link sent via e-mail
        return render_template('auth/reset.html', token = token)
    
    elif req.method == 'POST':
        password = req.form.get('password')
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User.query.filter(User.email == email).first()
        if not user:
            print("User not found !!!!!!!!!!!!!!!!!")
        else:
            print("User Found !")
            
        user.password = hashedPassword
        

        
        db.session.commit()
        
        print("Password updated !")
        flash("Your Password has been updated !")
        return redirect(url_for('auth.login'))
    else:
        return "Invalid Request !"
    