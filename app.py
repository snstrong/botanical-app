import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
from models import db, connect_db, User, GrowingArea, PlantList, Plant, PlantList_Plants
from trefle_requests import quick_search, get_one_plant
from forms import UserAddForm, UserEditForm, LoginForm, GrowingAreaForm, NewPlantListForm, AddPlantForm
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

def username_match(username):
    """Check to see if a username matches g.user.username. Returns True or False."""
    g_user = check_if_g_user()
    if not g_user:
        return False
    else:
        if g_user.username == username:
            return True

#############################################################
# General Routes
#############################################################

@app.route('/')
def show_landing_page():
    if g.user:
        return redirect(f"/{g.user.username}/garden")
    return render_template('index.html')

#############################################################
# Search Routes
#############################################################

@app.route('/search')
def get_quick_search_results():
    """Show results for single-term search."""
    # TODO: refactor as JSON API endpoint; build page with JS; will make dealing with pagination more sensible
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
    """
    Show data for a given plant.
    If logged in user, give option to add to a plant list.
    """
    plant_details = get_one_plant(trefle_token, plant_slug)

    if g.user:
        add_plant_form = AddPlantForm()
        # Check to see if user has existing plant lists and populate select choices accordingly"""
        if g.user.plant_lists:
            plant_lists = [(list.id, list.name) for list in g.user.plant_lists]
            plant_lists.append(("0", "Create New List"))
            add_plant_form.plant_list.choices = plant_lists
        else:
            add_plant_form.plant_list.choices = [("0", "Create New List")]
        # Pass along data about plant in hidden fields
        add_plant_form.plant_id.data = plant_details["data"]["id"]
        add_plant_form.plant_slug.data = plant_details["data"]["slug"]
        add_plant_form.plant_scientific_name.data = plant_details["data"]["scientific_name"]
        if plant_details["data"]["image_url"]:
            add_plant_form.plant_image_url.data = plant_details["data"]["image_url"]
        else:
            add_plant_form.plant_image_url.data = "/static/images/thumbnail_default.png"
        return render_template('plant-detail.html', plant_details=plant_details, form=add_plant_form)
    
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
        flash("You are not authorized to access this page.", "warning")
        return redirect('/')

#############################################################
# Garden Routes
#############################################################

@app.route('/<username>/garden')
def show_garden_page(username):
    this_user = User.query.filter_by(username=username).first_or_404()
    growing_areas = GrowingArea.query.filter_by(user_id=this_user.id).all()
    plant_lists = PlantList.query.filter_by(user_id=this_user.id).all()
    for p_list in plant_lists:
        if p_list.growing_area:
                growing_area = GrowingArea.query.get_or_404(p_list.growing_area)
                p_list.growing_area = growing_area.name
    return render_template("user-garden.html", growing_areas=growing_areas, plant_lists=plant_lists, username=username)

#############################################################
# Growing Area Routes
#############################################################

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
                user_id = session[CURR_USER_KEY],
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
            if g.user:
                return redirect("/{g.user.username}/garden")
            else:
                return redirect("/")
        
        flash("Successfully created new growing area!", "success")
        return redirect(f"/{g.user.username}/garden")

    return render_template("growing-areas/new-growing-area.html", form=form)


@app.route('/<username>/edit-growing-area/<int:growing_area>', methods=['PATCH'])
def edit_growing_area(username, growing_area):
    # TODO: flesh this out
    pass;

@app.route('/<username>/delete-growing-area/<int:growing_area>', methods=['DELETE'])
def delete_growing_area(username, growing_area):
    # TODO: flesh this out
    pass;

#############################################################
# Plant List Routes
#############################################################

@app.route('/<username>/new-plant-list', methods=['GET', 'POST'])
def new_plant_list(username):
    """Renders form to create new plant list. Handles form submission."""
    if not username_match(username):
        flash("Not authorized.", "warning")
        return redirect('/')
    
    form = NewPlantListForm()
    
    # Generate choices for select field
    growing_areas = g.user.growing_areas
    if growing_areas:
        growing_area_names = [(area.id, area.name) for area in growing_areas]
        growing_area_names.insert(0, (0, "(none)"))
    else:
        growing_area_names = [(0, "(none)")]
    form.growing_area.choices = growing_area_names


   # TODO: check for edge case (User already has plant list with same name)

    if form.validate_on_submit():   
        db.session.rollback()
        try:
            plant_list = PlantList(
                user_id = int(session[CURR_USER_KEY]),
                name = form.name.data,
                description = form.description.data
            )
            if int(form.growing_area.data) > 0 and form.growing_area.data is not None:
                plant_list.growing_area = int(form.growing_area.data)
            db.session.add(plant_list)
            db.session.commit()

        except IntegrityError:
            flash("Sorry, something went wrong.", 'warning')
            if g.user:
                return redirect(f"/{g.user.username}/garden")
            else:
                return redirect("/")
        
        flash("Successfully created new plant list!", "success")
        return redirect(f"/{g.user.username}/garden")

    return render_template("plant-lists/new-plant-list.html", form=form)


# TODO: All of these

# Show plant list
# /username/plant-list/plant-list-id

@app.route('/<username>/plant-list/<int:plant_list_id>')
def show_plant_list(username, plant_list_id):
    plant_list = PlantList.query.get_or_404(plant_list_id)
    if plant_list.growing_area:
        growing_area = GrowingArea.query.get_or_404(plant_list.growing_area)
        growing_area_name = growing_area.name
        return render_template('/plant-lists/plant-list-detail.html', plant_list=plant_list, username=username, growing_area_name=growing_area_name)
    else:
        return render_template('/plant-lists/plant-list-detail.html', plant_list=plant_list, username=username)
        

# Add Plant to List
@app.route('/<username>/plant-list/add-plant', methods=['POST'])
def add_plant_to_list(username):
    if not username_match(username):
        flash("Not authorized.", "warning")
        redirect("/")
    
    form = AddPlantForm(request.form)
    form.plant_id.data = int(form.plant_id.data)
    print("Plant ID", form.plant_id.data)
    print("Plant slug", form.plant_slug.data)
    print("Plant scientific name", form.plant_scientific_name.data)

    # TODO: TypeError: 'NoneType' object is not iterable. But if you look at form, all of the necessary data is there. This error only happens when the form is validated, like so:
    # if form.validate_on_submit():
    # The error goes away if we change it to the following:
    if form:   
    
        db.session.rollback()
        try:
            # Check to see if plant is already in plants table
            # If not, add it to plants table 
            plant = None
            if Plant.query.get(form.plant_id.data):
                plant = Plant.query.get(form.plant_id.data)
            else:
                plant = Plant(
                    id = form.plant_id.data,
                    slug = form.plant_slug.data,
                    scientific_name = form.plant_scientific_name.data,
                    image_url = form.plant_image_url.data
                )
            db.session.add(plant)
            db.session.commit()

            # Add plant and plant list to join table
            plant_on_list = PlantList_Plants(
                plant_list_id = form.plant_list.data,
                plant_id = plant.id
            )
            db.session.add(plant_on_list)
            db.session.commit()
            flash(f"Plant successfully added to list!")

        except IntegrityError:
            flash("Sorry, something went wrong.", 'warning')
            if g.user:
                return redirect(f"/{g.user.username}/garden")
            else:
                return redirect("/")
    return redirect(f"/{g.user.username}/garden")
    

# Delete Plant from List
# /username/plant-list/id/delete-plant

# Assign List to Growing/Planting Area
# /username/plant-list/id/add-plant

