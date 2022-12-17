from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'

db = SQLAlchemy(app)

class Player(db.Model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(20))

class AllTimePlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
