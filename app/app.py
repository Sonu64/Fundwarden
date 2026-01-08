from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_mail import Mail
import os

# Initialize globals (without app)
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # --- Fetch variables INSIDE the function ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Mail Configuration ---
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('APP_EMAIL_PASSWORD')

    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    loginManager = LoginManager()
    loginManager.init_app(app)
    loginManager.login_view = 'auth.login'

    from app.blueprints.auth.models import User
    @loginManager.user_loader
    def loadUser(userID):
        return User.query.get(int(userID))

    # --- Blueprints ---
    from app.blueprints.auth.routes import auth
    from app.blueprints.core.routes import core
    
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(core, url_prefix='/app')

    return app