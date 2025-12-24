from flask import Blueprint, render_template, Flask, request as req, redirect, url_for, flash
from flask import jsonify
#Import DB and DB Models
from app.app import db, bcrypt, mail
from app.blueprints.auth.models import User
# Import Authentication modules from flask_login
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
import re

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
        return render_template('auth/login.html', email = "", password = "")
    elif req.method == 'POST':
        email = req.form.get('email')
        password = req.form.get('password')
        
        if email.strip() == "" or len(password) == 0:
            flash("Please Provide an E-Mail Address and Password", "danger")
            return render_template('auth/login.html', email = email, password = password)
        
        # Get Row for the Username
        userRow = User.query.filter(User.email == email).first()
        # User doesn't exist
        if not userRow:
            flash("E-Mail does not exist !", "danger")
            return render_template('auth/login.html', email = email, password = password)
        hashedPassword = userRow.password
        # Check hashed password
        passwordMatched = bcrypt.check_password_hash(hashedPassword, password)
        # Password doesn't match
        if not passwordMatched:
            flash("Wrong Password !", "danger")
            return render_template('auth/login.html', email = email, password = password)
        else:
            login_user(userRow) # Cookie with userID: <userID> saved but will not persist to subsequent requests if LoginManager.user_loader is not properly configured.
            # login_user() finds the ID with the .get_id attribute provided by UserMixin
            flash("Logged In Successfully !", "success")
            return redirect(url_for('core.index'))
    else:
        return "Invalid Request !"
    

# url_for('core.register') ---> Points to the register route handler of the Core BP. 
@auth.route("/register", methods = ['GET', 'POST'])
def register():
    if req.method == 'GET':
        return render_template('auth/register.html', email="", name="", password="", confirm="")
    elif req.method == 'POST':
        email = req.form.get("email")
        name = req.form.get("name")
        password = req.form.get("password")
        confirm = req.form.get("confirm")
        
        if email.strip()=="" or name.strip=="":
            flash("Please Provide a Valid E-Mail address and your Full-name !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = password, confirm = confirm)
        
        # Fullname regex
        nameRegex = r"^[A-Z][a-z]*(?:[\s'-][A-Z][a-z]*)*$"
        passwordRegex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"   
        
        
        #Checking for Uniqueness of the Username
        existingUser = User.query.filter(User.email == email).first()
        if existingUser:
            flash("E-Mail already exists !", "danger")
            return render_template("auth/register.html", email = email, name = name, password = password, confirm = confirm)
        
        if not re.match(nameRegex, name):
            flash("Full Name must contain your First and Last names starting with capital letters, seperated by Space, no numbers allowed !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = password, confirm = confirm)
                   
        if not re.match(passwordRegex, password):
            flash("Password must contain more than 6 characters, at least One uppercase letter, a number and a special character !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = password, confirm = confirm)     
        
        if password != confirm:
            flash("Passwords don't match !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = password, confirm = confirm) 
                                                           

        ## When every condiition above doesn't hold true ##
        

        # Hashing Password
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        userObject = User(email = email, name = name, password = hashedPassword, balance = 1000)
        db.session.add(userObject)
        db.session.commit()
        flash("Registration Successful ! You can Log In now 😊", 'success')
        return redirect(url_for('auth.login')) 
    else:
        return "Invalid Request !"
    

@auth.route("logout")
def logout():
    logout_user()
    flash("Logged Out Successfuly !", "success")
    return redirect(url_for('auth.index')) # Landing Page


@auth.route("forgotPassword", methods = ['GET', 'POST'])
def forgotPassword():
    if req.method == 'GET':
        return render_template('auth/forgot.html', email = "")
    elif req.method == 'POST':
        email = req.form.get("email")
        if email.strip() == "":
            flash("Please provide an E-Mail Address !", "danger")
            return render_template('auth/forgot.html', email = "")
        foundUser = User.query.filter(User.email == email).first() # self in non-static methods represents this Live Row from the Users Table
        try:
            # Generate Reset Token, from user specific generateResetToken() function, which gets access to current user's email via self.email. But if we had made it a static method, we had to pass queried user from here. But being a normal method, it gets to user via self.
            token = foundUser.generateResetToken() 
            resetLink = url_for('auth.resetPassword', token = token, _external = True)
            # Send Reset Link via E-Mail
            msg = Message("Password Reset Request", sender = "sonusantu64@gmail.com", recipients = [email])
            msg.body = f"Fundwarden Password Reset Link: {resetLink}"
            mail.send(msg)
            flash("Password Reset Link Sent to your E-Mail, please check your Inbox.", "info")
            print("Mail Sent !")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("If any account with that E-Mail exists, Password Reset Link was sent to that E-Mail, please check your Inbox.", "info")
            return render_template('auth/login.html', email = "", password = "")
    else:
        return "Invalid Request !"
    

# Use the Token as an URL Parameter to generate different reset links for different users
@auth.route("resetPassword/<token>", methods = ['GET', 'POST'])
def resetPassword(token):
    email = User.verifyResetToken(token) # Decode the E-Mail part from the token
    user = User.query.filter(User.email == email).first()
    
    if not email or not user:
        flash("Invalid E-Mail Address or Token Expired !", "danger")
        return redirect(url_for('auth.forgotPassword'))
    
    if req.method == 'GET':
        # A Valid GET request, matching the URL syntax can only be sent by clicking on the Link sent via e-mail
        return render_template('auth/reset.html', token = token, password = "", confirm = "")
    
    elif req.method == 'POST':
        password = req.form.get('password')
        confirm = req.form.get('confirm')
        passwordRegex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
        
        if not re.match(passwordRegex, password):
            flash("Password must contain more than 6 characters, at least One uppercase letter, a number and a special character !", 'danger')
            return render_template('auth/reset.html', token = token, password = password, confirm = confirm)
        
        if password != confirm:
            flash("Passwords Don't match !", "danger")
            return render_template('auth/reset.html', token = token, password = password, confirm = confirm)
            
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashedPassword
        db.session.commit()
        print("Password updated !")
        flash("Your Password has been updated !", "success")
        return redirect(url_for('auth.login'))
    else:
        return "Invalid Request !"
    