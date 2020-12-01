"""Seed database for Tendril."""

from app import db
from models import User


db.drop_all()
db.create_all()

db.session.commit()
