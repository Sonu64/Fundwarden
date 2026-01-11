from flask import Blueprint, render_template, Flask, request as req, redirect, url_for, flash, current_app
from flask import jsonify
#Import DB and DB Models
from app.app import db, bcrypt, mail
from app.blueprints.auth.models import User
# Import Authentication modules from flask_login
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
import re
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os



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
    if current_user.is_authenticated:
        flash("You are already Logged In !", 'info')
        return redirect(url_for('core.index'))
    if req.method == 'GET':
        return render_template('auth/login.html', email = "", password = "")
    elif req.method == 'POST':
        email = req.form.get('email')
        password = req.form.get('password')
        emailRegex  = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if email.strip() == "" or len(password) == 0 or not re.match(emailRegex, email):
            flash("Please Provide a valid E-Mail Address and Password", "danger")
            return render_template('auth/login.html', email = email, password = "")
        
        # Get Row for the Username
        userRow = User.query.filter(User.email == email).first()
        # User doesn't exist
        if not userRow:
            flash("E-Mail does not exist !", "danger")
            return render_template('auth/login.html', email = email, password = "")
        hashedPassword = userRow.password
        # Check hashed password ------- INVALID SALT ERROR !!!!!!!!!
        passwordMatched = bcrypt.check_password_hash(hashedPassword, password)
        # Password doesn't match
        if not passwordMatched:
            flash("Wrong Password !", "danger")
            return render_template('auth/login.html', email = email, password = "")
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
    if current_user.is_authenticated:
        flash("You are already Logged In !", 'info')
        return redirect(url_for('core.index'))
    if req.method == 'GET':
        return render_template('auth/register.html', email="", name="", password="", confirm="")
    elif req.method == 'POST':
        email = req.form.get("email")
        name = req.form.get("name")
        name = name.strip()
        password = req.form.get("password")
        confirm = req.form.get("confirm")
        emailRegex  = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if email.strip()=="" or name.strip=="" or not re.match(emailRegex, email):
            flash("Please Provide a Valid E-Mail address and your Full-name !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = password, confirm = confirm)
        
        # Fullname regex
        nameRegex = r"^[A-Z][a-zA-Z]*(?:\s[A-Z][a-zA-Z]*)+$"
        passwordRegex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"   
        
        
        #Checking for Uniqueness of the Username
        existingUser = User.query.filter(User.email == email).first()
        if existingUser:
            flash("E-Mail already exists !", "danger")
            return render_template("auth/register.html", email = email, name = name, password = "", confirm = "")
        
        if not re.match(nameRegex, name):
            flash("Full Name must contain your First and Last names starting with capital letters, seperated by Space, no numbers allowed !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = "", confirm = "")
                   
        if not re.match(passwordRegex, password):
            flash("Password must contain more than 6 characters, at least One uppercase letter, a number and a special character !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = "", confirm = "")     
        
        if password != confirm:
            flash("Passwords don't match !", 'danger')
            return render_template('auth/register.html', email = email, name = name, password = "", confirm = "") 
                                                           

        ## When every condiition above doesn't hold true ##
        token = User.generateEmailConfirmToken(email, name, password) 
        confirmLink = url_for('auth.confirmEmail', token = token, _external = True)
        # Send Reset Link via E-Mail
        # --- BREVO API INTEGRATION ---
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        # Construct the recipient and sender
        to = [{"email": email, "name": name}]
        sender = {"name": "Fundwarden", "email": current_app.config['MAIL_DEFAULT_SENDER']}
        # 1. Create the message object
        # Create the email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            reply_to={"email": "sonusantu64@gmail.com", "name": "Fundwarden E-Mail Verification"},
            subject="Verify Your Fundwarden Account",
            html_content=f"""
            <html>
                <body>
                    <h1>Welcome to Fundwarden!</h1>
                    <p style = "font-size:18px;margin-bottom:40px;">Click the link below to Verify your E-Mail Address.</p>
                    <a href="{confirmLink}" style="color:white;border: 2px solid white;background-color:#00a452;font-weight:bold;text-decoration:none; padding: 16px 18px;font-family:sans-serif;margin:20px 0;font-size:18px;">Confirm E-Mail Address</a>
                    <p style="font-size:18px;margin-top:40px">If you did not request this, please ignore this email.</p>
                </body>
            </html>
            """
        )

        try:
            # This API call is much faster than SMTP and won't timeout
            api_instance.send_transac_email(send_smtp_email)
            flash("A Verification Link has been sent to your ✉︎ E-Mail. Please check your Inbox or Spam Folder.", "info")
        except ApiException as e:
            print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
            flash("Account created, but we had trouble sending the verification email.", "warning")
        return redirect(url_for('auth.login'))
        
    else:
        return "Invalid Request !"
    

@auth.route("logout")
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfuly !", "success")
    return redirect(url_for('auth.index')) # Landing Page


@auth.route("forgotPassword", methods = ['GET', 'POST'])
def forgotPassword():
    if current_user.is_authenticated:
        flash("You are already Logged In, Please Logout to reset password !", 'info')
        return redirect(url_for('core.index'))
    if req.method == 'GET':
        return render_template('auth/forgot.html', email = "")
    elif req.method == 'POST':
        email = req.form.get("email")
        if email.strip() == "":
            flash("Please provide an E-Mail Address !", "danger")
            return render_template('auth/forgot.html', email = email)
        foundUser = User.query.filter(User.email == email).first() # self in non-static methods represents this Live Row from the Users Table
        # Generate Reset Token, from user specific generateResetToken() function, which gets access to current user's email via self.email. But if we had made it a static method, we had to pass queried user from here. But being a normal method, it gets to user via self.
        token = foundUser.generateResetToken() 
        resetLink = url_for('auth.resetPassword', token = token, _external = True)
        # --- BREVO API INTEGRATION ---
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": foundUser.email}],
        sender={"name": "Fundwarden Support", "email": current_app.config['MAIL_DEFAULT_SENDER']},
        reply_to={"email": "sonusantu64@gmail.com", "name": "Fundwarden Password Reset"},
        subject="Password Reset Request",
        html_content=f"""
        <html>
            <body>
                <p style="font-size:18px;">You requested a Password Reset for your Fundwarden account.</p>
                <p style = "font-size:18px;margin-bottom:40px;">Click the link below to set a new password:</p>
                <a href="{resetLink}" style="color:white;border: 2px solid white;background-color:#ff6f00;font-weight:bold;text-decoration:none; padding: 16px 18px;font-family:sans-serif;margin:20px 0;font-size:18px;">Reset My Password</a>
                <p style="font-size:18px;margin-top:40px">If you did not request this, please ignore this email.</p>
            </body>
        </html>
        """
    )

        try:
            api_instance.send_transac_email(send_smtp_email)
            flash("A password reset link has been sent to your email.", "info")
        except ApiException as e:
            print(f"Error sending password reset: {e}")
            flash("Could not send reset email. Please try again later.", "danger")
        return redirect(url_for('auth.login'))
    else:
            return "Invalid Request !"
    


@auth.route("resetPassword/<token>", methods = ['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        flash("You are already Logged In !", 'info')
        return redirect(url_for('core.index'))
    email = User.verifyResetToken(token) # Decode the E-Mail part from the token
    user = User.query.filter(User.email == email).first()
    
    if not email or not user:
        flash("Invalid E-Mail Address or Token Expired !", "danger")
        return redirect(url_for('auth.forgotPassword'))
    
    if req.method == 'GET':
        
        return render_template('auth/reset.html', token = token, password = "", confirm = "")
    
    elif req.method == 'POST':
        password = req.form.get('password')
        confirm = req.form.get('confirm')
        passwordRegex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
        
        if not re.match(passwordRegex, password):
            flash("Password must contain more than 6 characters, at least One uppercase letter, a number and a special character !", 'danger')
            return render_template('auth/reset.html', token = token, password = "", confirm = "")
        
        if password != confirm:
            flash("Passwords Don't match !", "danger")
            return render_template('auth/reset.html', token = token, password = "", confirm = "")
            
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashedPassword
        db.session.commit()
        print("Password updated !")
        flash("Your Password has been updated !", "success")
        return redirect(url_for('auth.login'))
    else:
        return "Invalid Request !"
    
    
    
@auth.route('features')
def features():
    return render_template('auth/features.html')


@auth.route('credits')
def credits():
    return render_template('auth/credits.html')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@auth.route("confirmEmail/<token>", methods = ['GET'])
def confirmEmail(token):

    if req.method == 'GET':
        payload = User.verifyEmailConfirmToken(token) # Decode the payload dict. part from the token
        if not payload:
            flash("Link Expired !", 'danger')
            return redirect(url_for('auth.register'))
        print(payload)
        user = User.query.filter(User.email == payload['email']).first()
    
        if user:        
            flash("Can't Verify E-Mail as this E-mail is already linked to an account !", "danger")
            return redirect(url_for('auth.register'))
        
        # Process of putting Data in Database
        email = payload['email']
        name = payload['name']
        hashedPassword = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
        userObject = User(email=email, name=name, password=hashedPassword, balance=0)
        try:
            db.session.add(userObject)
            db.session.commit()        
            flash("E-Mail Verified ! You can Login now 😀", 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("Some Error occured while Registering !", 'danger')
            print("\n\n\n" + str(e) + "\n\n\n")
            return redirect(url_for('auth.register'))
    else:
        return "Invalid Request !"
    
    
