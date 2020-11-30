"""Functions for making requests to Trefle API."""

import requests
from secrets import trefle_token

BASE_URL = "https://trefle.io"

def quick_search(token, search_term):
    """Simple single-field search request. Returns JSON response as dict."""
    response = requests.get(f'{BASE_URL}/api/v1/species/search', params={"q": search_term, "token": token})
    return response.json()["data"]

def get_next_page(token, search_response):
    if search_response.links.next:
        response = requests.get(f'{BASE_URL}{search_response.links.next}', params={"token": token})
    else:
        response = requests.get(f'{BASE_URL}{search_response.links.last}', params={"token": token})
    return response.json()["data"]

def get_one_plant(token, plant_slug):
    """Retrieves data for a specific plant. Returns JSON response as dict."""
    response = requests.get(f'{BASE_URL}/api/v1/species/{plant_slug}', params={"token": token})
    return response.json()["data"]


advanced_search_tester = {
    "range[maximum_height_cm]": "20,120",
    "filter[flower_color]": "red",
    "filter[flower_conspicuous]": "true"
}

def advanced_search(token, search_terms):
    """Multi-field search request to API. Returns JSON response as dict."""
    search_terms["token"] = token
    response = requests.get(f'{BASE_URL}/api/v1/species', params=search_terms)
    return response.json()["data"]

