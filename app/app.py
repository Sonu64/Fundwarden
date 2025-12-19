from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

# Factory function
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./fundwarden.db"
    db.init_app(app)
    
    from app.blueprints.auth.routes import auth # This is the key for Flask to automatically find url_for('core.login') from inside the core folder, and check for @core.route("/login") in routes.py and not in some other file like models.py. Now core. represents the file content of routes.py inside the core folder
    # !!! Route wale file se Blueprint name ko import karo !!!!
    
    app.register_blueprint(auth, url_prefix = "/")
    
    return app