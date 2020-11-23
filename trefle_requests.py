"""Functions for making and handling requests to Trefle API."""

import requests
from secrets import trefle_token

BASE_URL = "https://trefle.io/api/v1"

def simple_search(token, search_term):
    """Simple single-field search request"""
    response = requests.get(f'{BASE_URL}/species/search', params={"q": search_term, "token": token})
    return response.json()["data"]

def get_one_plant(token, plant_slug):
    """Retrieves data for a specific plant."""
    # https://trefle.io/api/v1/species/lobelia-cardinalis?token=_aqxCyNPL9F16KUr6xINkPYqGNvZjnicOHyKYcw1ITg
    response = requests.get(f'{BASE_URL}/species/{plant_slug}', params={"token": token})
    return response.json()["data"]