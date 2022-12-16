from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
import argparse
from player_rating_refresh import PlayerRatingClass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)

class PlayerRating(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/user', methods=['POST'])
def user_redirect():
    if request.method == 'POST':
        connect_code = request.form['connect_code'].replace("#","-").upper()
        return redirect('/user/' + str(connect_code))

@app.route('/user/<connect_code>', methods=['POST','GET'])
def user(connect_code):
    connect_code = connect_code.replace("-","#").upper()
    player_rating_class = PlayerRatingClass()
    player_rating_class.insert_new_rating(connect_code)

    player_ratings = PlayerRating.query.where(PlayerRating.connect_code.ilike(connect_code)).order_by(PlayerRating.datetime).limit(10).all()
    datetimes = []
    ratings = []
    for rating in player_ratings:
        datetimes.append(rating.datetime.strftime("%m/%d/%Y, %H:%M:%S"))
        ratings.append(rating.rating)
    
    context = {
        "player_ratings": player_ratings,
        "connect_code": connect_code,
        "datetimes": datetimes,
        "ratings": ratings
    }

    return render_template('user.html', **context)

@app.route('/all_ratings', methods=['GET'])
def all_ratings():
    player_ratings = PlayerRating.query.order_by(PlayerRating.datetime).all()
    return render_template('all_ratings.html', player_ratings=player_ratings)

if __name__ == '__main__':
    app.run(debug=True)