from sqlalchemy.sql import func
from . import db

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(255))
    html = db.Column(db.Text, unique=True, nullable=False)