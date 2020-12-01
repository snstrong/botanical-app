import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
from models import db, connect_db, User
from trefle_requests import quick_search, get_one_plant
from forms import UserAddForm, UserEditForm
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///botanical'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
toolbar = DebugToolbarExtension(app)
trefle_token = os.environ.get('TREFLE_TOKEN')

connect_db(app)

#############################################################
# User signup/login/logout
#############################################################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

#############################################################
# General Routes
#############################################################

@app.route('/')
def show_landing_page():
    return render_template('index.html')

@app.route('/search')
def get_quick_search_results():
    """Show results for single-term search."""
    
    # TODO: handle edge case: no results found
    # TODO: check for image and provide default if null
    # TODO: get next page of results ("Show more results" or continuous scroll)
    search_term = request.args['term']
    search_results = quick_search(trefle_token, search_term)
    return render_template('search-results.html', search_term=search_term, search_results=search_results)

@app.route('/plant/<plant_slug>')
def get_plant_detail(plant_slug):
    """Show data for a given plant."""
    plant_details = get_one_plant(trefle_token, plant_slug)
    return render_template('plant-detail.html', plant_details=plant_details)

#############################################################
# User Routes
#############################################################

@app.route('/register', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If data from form not valid, re-render form.

    If there is already a user with that username, flash message
    and re-render form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('register.html', form=form)


# @app.route('/login', methods=["GET", "POST"])
# def login():
#     """Handle user login."""

#     form = LoginForm()

#     if form.validate_on_submit():
#         user = User.authenticate(form.username.data,
#                                  form.password.data)

#         if user:
#             do_login(user)
#             flash(f"Hello, {user.username}!", "success")
#             return redirect("/")

#         flash("Invalid credentials.", 'danger')

#     return render_template('login.html', form=form)


# @app.route('/logout')
# def logout():
#     """Handle logout of user."""
#     do_logout()
#     flash('You have been logged out.', 'warning')
#     return redirect('/login')
