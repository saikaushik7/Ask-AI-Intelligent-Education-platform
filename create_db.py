from app import app
from models import db

with app.app_context():
    print("Creating DB...")
    db.create_all()
    print("DB created successfully!")


# this file can be deleted later