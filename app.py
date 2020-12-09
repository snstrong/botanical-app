import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
from models import db, connect_db, User, GrowingArea
from trefle_requests import quick_search, get_one_plant
from forms import UserAddForm, UserEditForm, LoginForm, GrowingAreaForm
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

def check_if_g_user():
    """Check to see if there is a user in Flask global. If so, return g.user, else return False."""
    if g.user:
        return g.user
    else:
        return False



#############################################################
# General Routes
#############################################################

@app.route('/')
def show_landing_page():
    return render_template('index.html')

#############################################################
# Search Routes
#############################################################

@app.route('/search')
def get_quick_search_results():
    """Show results for single-term search."""
    # TODO: refactor as JSON API endpoint; build page with JS; will make dealing with pagination more sensible
    # TODO: handle edge case: no results found
    # TODO: check for image and provide default if null
    # TODO: get next page of results ("Show more results" or continuous scroll)
    search_term = request.args['term']
    search_results = quick_search(trefle_token, search_term)
    return render_template('search-results.html', search_term=search_term, search_results=search_results)

@app.route('/search/next', methods=['GET'])
def get_next_results_page():
    """Get next page of search results. Return as JSON."""
    pass;

@app.route('/search/advanced', methods=['GET'])
def get_advanced_search_results():
    """Handle advanced search request. Return JSON."""
    pass;

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


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash('You have been logged out.', 'warning')
    return redirect('/login')

@app.route('/<username>/account')
def show_account_info(username):
    if g.user and g.user.username == username:
        return render_template('user-account.html')
    else:
        flash("You are not authorized to access this page.")
        return redirect('/')

@app.route('/<username>/garden')
def show_garden_page(username):
    growing_areas = GrowingArea.query.filter_by(user=g.user.id).all()
    return render_template("user-garden.html", growing_areas=growing_areas)

@app.route('/<username>/growing-area/<int:growing_area>')
def show_growing_area(username, growing_area):
    pass;

@app.route('/<username>/new-growing-area', methods=['GET', 'POST'])
def create_growing_area(username):
    """Render form for creating a new growing area in the user's garden"""
    
    if not g.user or g.user.username != username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = GrowingAreaForm()

    if form.validate_on_submit():
        try:
            growing_area = GrowingArea(
                user = session[CURR_USER_KEY],
                name = form.name.data,
                description = form.description.data,
                light_level = form.light_level.data,
                soil_texture = form.soil_texture.data,
                soil_moisture = form.soil_moisture.data,
                soil_ph = form.soil_ph.data,
                notes = form.notes.data
            )
            db.session.add(growing_area)
            db.session.commit()

        except IntegrityError:
            flash("Sorry, something went wrong. Please try again.", 'danger')
            return render_template('register.html', form=form)
        flash("Successfully created new growing area!", "success")
        return redirect("/{g.user}/garden")

    return render_template("growing-areas/new-growing-area.html", form=form)


@app.route('/<username>/edit-growing-area/<int:growing_area>', methods=['PATCH'])
def edit_growing_area(username, growing_area):
    pass;

@app.route('/<username>/delete-growing-area/<int:growing_area>', methods=['DELETE'])
def delete_growing_area(username, growing_area):
    pass;


