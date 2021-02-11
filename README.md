# Tendril
### A botanical web app for gardeners
[https://tendril-botanical-app.herokuapp.com/](https://tendril-botanical-app.herokuapp.com/)

**Tendril** is intended as a research and planning tool for the home gardener. Anyone can use Tendril to search for information about plants, and with an account, users can save lists of plants as well as information about the planting areas they have available in their garden, like light level and soil type. Plant lists can be assigned to planting areas to describe what is already there or to make plans for the future.

## User Flow
* Landing Page - Users can search for plants, register, or log-in
* Search form on all other pages on nav bar, which also links to registration and login for non-logged-in users, or to the Garden page and logout for logged-in users
* Logged-in users will be taken to their Garden page, which displays their Planting Areas and Plant Lists, and options to create new Planting Areas and Plant Lists
* Searching for plants will display results that link to individual plant pages with more information about each species. Logged-in users can add plants to a list from individual plant pages

## Tech Stack
* Python/Flask back-end
* HTML5/CSS3 with Jinja and Bootstrap front-end
* Bcrypt for hashing and authentication
* PostgreSQL relational database with Flask-SQLAlchemy ORM
* Logo Design with Adobe Illustrator

This project uses data from the **Trefle global plants API**
* [https://trefle.io/](https://trefle.io/)
* GitHub: https://github.com/treflehq
