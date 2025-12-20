from flask import Blueprint, render_template, Flask, request as req, redirect, url_for
from flask import jsonify
#Import DB and DB Models
from app.app import db, bcrypt
from app.blueprints.auth.models import User
# Import Authentication modules from flask_login
from flask_login import login_user, logout_user, current_user, login_required

core  = Blueprint('core', __name__)

@core.route('/') # /app
@login_required
def index():
    return render_template('/core/index.html', user = current_user)