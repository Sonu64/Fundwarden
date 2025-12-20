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

@core.route('add', methods = ['GET', 'POST'])
@login_required
def add():
    if req.method == 'GET':
        return render_template('/core/add.html')
    elif req.method == 'POST':
        cash = req.form.get('cash')
        newBalance = int(cash) + int(current_user.balance)
        # current_user directly Refers to that Row, if we change values for current_user and commit to DB,
        # the changes take effect in the main Database as well. It represents a "LIVE row in the DB, not just a copy"
        # Even though current_user "refers to that row," the changes only hit the main database file when you call db.session.commit().
        current_user.balance = newBalance
        db.session.commit()
        return redirect(url_for('core.index'))
    else:
        return "Invalid Request !"
    
    
@core.route('/allocator')
@login_required
def allocator():
    return render_template('core/allocator.html')


@core.route('/tracker')
@login_required
def tracker():
    return render_template('core/tracker.html')