from flask import Flask, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt  # Import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy() # DB Instance globally
bcrypt = Bcrypt() # Bcrypt Instance globally

# Factory function
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./fundwarden.db"
    app.secret_key = "ds#*&@^80f90$%^@09_8@89xn83928_8(*2*^73)"
    
    db.init_app(app)
    bcrypt.init_app(app)
    
    loginManager = LoginManager()
    loginManager.init_app(app)
    loginManager.login_view = 'auth.login' # Page to Load when unauthorized users wanna access Protected Routes
    
    
    from app.blueprints.auth.models import User
    # Tell Login Manager using the function below that how it should Load users
    @loginManager.user_loader
    def loadUser(userID):
        return User.query.get(userID)
    
    
    from app.blueprints.auth.routes import auth # This is the key for Flask to automatically find url_for('core.login') from inside the core folder, and check for @core.route("/login") in routes.py and not in some other file like models.py. Now core. represents the file content of routes.py inside the core folder
    # !!! Route wale file se Blueprint name ko import karo !!!!
    from app.blueprints.core.routes import core
    
    app.register_blueprint(auth, url_prefix = "/")
    app.register_blueprint(core, url_prefix = '/app')
    
    migrate = Migrate(app, db)
    
    return app