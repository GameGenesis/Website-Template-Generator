from . import db
from sqlalchemy.ext.mutable import MutableList

pickle_type = MutableList.as_mutable(db.PickleType())

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(255))
    html = db.Column(db.Text, unique=True, nullable=False)
    simplified_message_history = db.Column(pickle_type, nullable=True)
    full_message_history = db.Column(pickle_type, nullable=True)
    db.Column(db.ARRAY(db.String(255)))