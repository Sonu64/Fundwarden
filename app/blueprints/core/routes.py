from flask import (
    Blueprint,
    render_template,
    Flask,
    request as req,
    redirect,
    url_for,
)
from flask import jsonify, flash

# Import DB and DB Models
from app.app import db, bcrypt
from app.blueprints.core.models import Categories
from app.blueprints.auth.models import User

# Import Authentication modules from flask_login
from flask_login import login_user, logout_user, current_user, login_required

core = Blueprint("core", __name__)




















# ------------------------
# Main App Routes
# ------------------------
@core.route("/")  # /app
@login_required
def index():
    return render_template("/core/index.html", user=current_user)
















# ------------------------
# Budget Allocator Routes
# ------------------------

@core.route("add", methods=["GET", "POST"])
@login_required
def add():
    if req.method == "GET":
        return render_template("/core/add.html")
    elif req.method == "POST":
        cash = req.form.get("cash")
        newBalance = int(cash) + int(current_user.balance)
        # current_user directly Refers to that Row, if we change values for current_user and commit to DB,
        # the changes take effect in the main Database as well. It represents a "LIVE row in the DB, not just a copy"
        # Even though current_user "refers to that row," the changes only hit the main database file when you call db.session.commit().
        current_user.balance = newBalance
        db.session.commit()
        return redirect(url_for("core.index"))
    else:
        return "Invalid Request !"


@core.route("allocator")
@login_required
def allocator():
    categoriesList = giveCategoriesListOfDicts()
    return render_template(
        "core/allocator.html",
        categoriesList=categoriesList,
        category="",
        budget="",
    )


@core.route("createCategory", methods=["GET", "POST"])
@login_required
def createCategory():
    if req.method == "GET":
        # Possible only through Redirects to url_for('core.createCategory')
        return redirect(
            url_for("core.allocator")
        )  # category and budget handled by IF jinja syntax in core/allocator.html, same for categoriesList, these values can only be added by render_template, not redirect()
    elif req.method == "POST":
        categoryName = req.form.get("category")
        budget = req.form.get("budget")
        categoriesList = giveCategoriesListOfDicts()

        try:
            
            if int(budget) > current_user.balance:
                flash("You can't Add a Budget Exceeding your Current Balance !", "danger")
                return render_template(
                    "core/allocator.html",
                    categoriesList=categoriesList,
                    category=categoryName,
                    budget="",
                )
                
            
            if categoryName.strip() == "":
                flash("Please Provide a Category name !", "danger")
                return render_template(
                    "core/allocator.html",
                    categoriesList=categoriesList,
                    category="",
                    budget=budget,
                )

            if int(budget) == 0:
                flash("Please Provide a Budget amount !", "danger")
                return render_template(
                    "core/allocator.html",
                    categoriesList=categoriesList,
                    category=categoryName,
                    budget="",
                )
        except (ValueError, TypeError):
            flash("Please provide a Numeric Value for the Budget !", "danger")
            return render_template(
                "core/allocator.html",
                categoriesList=categoriesList,
                category=categoryName,
                budget="",
            )

        categoryName = categoryName.strip()

        userID = current_user.id
        spent = 0
        remaining = budget

        categoryObj = Categories(
            userID=userID,
            name=categoryName,
            budget=budget,
            spent=spent,
            remaining=remaining,
        )

        db.session.add(categoryObj)
        db.session.commit()

        flash(f"Successfuly created Category {categoryName} !", "success")
        return redirect(url_for("core.allocator"))

    else:
        return "Invalid Request !"


@core.route("extend", methods=["GET", "POST"])
@login_required
def extend():
    categoriesList = giveCategoriesListOfDicts()
    if req.method == "GET":
        return render_template(
            "core/extend.html",
            categories=categoriesList,
            category="",
            extension="",
        )
    elif req.method == "POST":

        try:
            category = req.form.get("category")
            extension = int(req.form.get("extension"))
        except (ValueError, TypeError):
            flash("Numeric Value needed !", "danger")
            return render_template(
                "core/extend.html",
                categories=categoriesList,
                category="",
                extension="",
            )

        if not category or category.strip() == "":
            flash("Please Choose a Category !", "danger")
            return render_template(
                "core/extend.html",
                categories=categoriesList,
                category="",
                extension=extension,
            )
        if extension == 0:
            flash("Please Give a Valid Extension amount !", "danger")
            return render_template(
                "core/extend.html",
                categories=categoriesList,
                category=category,
                extension="",
            )

        filteredCategory = Categories.query.filter(
            Categories.name == category, Categories.userID == current_user.id
        ).first()
        # .first() or .all() is ALWAYS needed !!!!!!
        # .all() gives a List of Category Objects ---> all objects are Live Copies from the DB
        # .first() gives a Single Category Object ---> all objects are Live Copies from the DB

        if not filteredCategory:
            flash("Error while fetching category name !", "danger")
            return redirect(url_for("core.allocator"))

        filteredCategory.budget += int(extension)

        # db.session.add(filteredCategory) # No need as filteredCategory is a Live Copy of the Row, though
        # db.session.commit() is needed as below
        try:
            db.session.commit()
            flash(
                f"Extended your Budget for {filteredCategory.name} !",
                "success",
            )
            return redirect(url_for("core.allocator"))
        except:
            flash("Some Error Occured !", "danger")
            return redirect(url_for("core.allocator"))
    else:
        return "Invalid Request"










# ------------------------
# Expense Tracker Routes
# ------------------------
@core.route("tracker")
@login_required
def tracker():
    return render_template(
        "core/tracker.html", categoriesList=giveCategoriesListOfDicts()
    )


@core.route("addExpense", methods=["GET", "POST"])
@login_required
def addExpense():
    if req.method == "GET":
        return render_template(
            "core/addExpense.html",
            categoriesList=giveCategoriesListOfDicts(),
            category="",
            expense="",
        )
    elif req.method == "POST":
        try:
            category = req.form.get("category")
            expense = int(req.form.get("expense"))
        except (ValueError, TypeError):
            flash("Numeric Value needed !", "danger")
            return render_template(
                "core/addExpense.html",
                categoriesList=giveCategoriesListOfDicts(),
                category="",
                expense="",
            )

        if not category or category.strip() == "":
            flash("Please Choose a Category !", "danger")
            return render_template(
                "core/addExpense.html",
                categoriesList=giveCategoriesListOfDicts(),
                category="",
                expense=expense,
            )
        if expense == 0:
            flash("Please Give a Valid Expense amount !", "danger")
            return render_template(
                "core/addExpense.html",
                categoriesList=giveCategoriesListOfDicts(),
                category=category,
                expense="",
            )

        filteredCategory = Categories.query.filter(
            Categories.name == category, Categories.userID == current_user.id
        ).first()
        # .first() or .all() is ALWAYS needed !!!!!!
        # .all() gives a List of Category Objects ---> all objects are Live Copies from the DB
        # .first() gives a Single Category Object ---> all objects are Live Copies from the DB

        if not filteredCategory:
            flash("Error while fetching category name !", "danger")
            return redirect(url_for("core.addExpense"))

        try:
            if expense <= filteredCategory.remaining:
                filteredCategory.spent += expense
                filteredCategory.remaining -= expense
                db.session.commit()
                flash(f"Expense Added Successfully for {category} !", "success")
                return redirect(url_for("core.tracker"))
            else:
                flash(f"You can't Spend ₹{expense} on {category}, as you only have ₹{filteredCategory.remaining} to be spent for {category}", "danger")
                return redirect(url_for("core.tracker"))
        except:
            flash("Some Error occured while adding Expense! Sorry !", "danger")
            return redirect(url_for("core.tracker"))
    else:
        return "Invalid Request !"

















# ------------------------ #
# METHODS IRRESPECTIVE OF ROUTES #
# ------------------------ #

def giveCategoriesListOfDicts():
    """Give the List of Dictionaries containing each category and the respective allocated budget"""
    categories = Categories.query.filter(Categories.userID == current_user.id)
    categoriesList = []
    for c in categories:
        categoriesList.append(
            {"name": c.name, "budget": c.budget, "spent": c.spent}
        )
    return categoriesList
