import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from secrets import trefle_token, secret_key
import requests
from models import db, connect_db
from trefle_requests import quick_search

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///botanical'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secret_key)
toolbar = DebugToolbarExtension(app)

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
# Routes
#############################################################

@app.route('/')
def show_landing_page():
    return render_template('index.html')

@app.route('/search')
def get_quick_search_results():
    search_term = request.args['term']
    search_results = quick_search(trefle_token, search_term)
    return render_template('search-results.html', search_term=search_term, search_results=search_results)
