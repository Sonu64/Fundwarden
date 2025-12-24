from flask import Blueprint, render_template, Flask, request as req, redirect, url_for
from flask import jsonify, flash
#Import DB and DB Models
from app.app import db, bcrypt
from app.blueprints.core.models import Categories
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
    
    
@core.route('allocator')
@login_required
def allocator():
    categories = Categories.query.filter(Categories.userID == current_user.id)
    categoriesList = []
    for c in categories:
        categoriesList.append({'name':c.name, 'budget':c.budget})
    return render_template('core/allocator.html', categoriesList = categoriesList, category = "", budget = "")


@core.route("createCategory", methods = ['GET', 'POST'])
@login_required
def createCategory():
    if req.method == 'GET':
        # Possible only through Redirects to url_for('core.createCategory')
        return redirect(url_for('core.allocator')) # category and budget handled by IF jinja syntax in core/allocator.html, same for categoriesList, these values can only be added by render_template, not redirect()
    elif req.method == 'POST':
        categoryName = req.form.get('category')
        budget = req.form.get('budget')
        print(categoryName, budget)
        if (categoryName.strip() == ""):
            flash("Please Provide a Category name !", "danger")
            categories = Categories.query.filter(Categories.userID == current_user.id)
            categoriesList = []
            for c in categories:
                categoriesList.append({'name':c.name, 'budget':c.budget})
            return render_template('core/allocator.html', categoriesList = categoriesList, category = "", budget = budget)
        
        if (int(budget) == 0):
            flash("Please Provide a Budget amount !", "danger")
            categories = Categories.query.filter(Categories.userID == current_user.id)
            categoriesList = []
            for c in categories:
                categoriesList.append({'name':c.name, 'budget':c.budget})
            return render_template('core/allocator.html', categoriesList = categoriesList, category = categoryName, budget = "")
        
        categoryName = categoryName.strip()
        
        userID = current_user.id
        spent = 0
        remaining = budget
        
        categoryObj = Categories(userID = userID, name = categoryName, budget = budget, spent = spent, remaining = remaining)
        
        db.session.add(categoryObj)
        db.session.commit()
        
        flash(f"Successfuly created Category {categoryName} !", "success")
        return redirect(url_for('core.allocator'))
        
    else:
        return "Invalid Request !"




@core.route('extend', methods = ['GET', 'POST'])
@login_required
def extend():
    if req.method == 'GET':
        categories = Categories.query.filter(Categories.userID == current_user.id)
        categoriesList = []
        for c in categories:
            categoriesList.append({'name':c.name, 'budget':c.budget})
        return render_template('core/extend.html', categories = categoriesList)
    elif req.method == 'POST':
        category = req.form.get('category')
        extension = req.form.get('extension')
        
        filteredCategory = Categories.query.filter(Categories.name==category, Categories.userID==current_user.id).first() 
        # .first() or .all() is ALWAYS needed !!!!!!
        # .all() gives a List of Category Objects ---> all objects are Live Copies from the DB
        # .first() gives a Single Category Object ---> all objects are Live Copies from the DB
        
        if not filteredCategory:
            return "Category Not found !"
        
        filteredCategory.budget += int(extension)
        
        # db.session.add(filteredCategory) # No need as filteredCategory is a Live Copy of the Row, though
        # db.session.commit() is needed as below
        db.session.commit()
        
        return redirect(url_for('core.allocator'))
    else:
        return "Invalid Request"
    







@core.route('tracker')
@login_required
def tracker():
    return render_template('core/tracker.html')