from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
import argparse
from player_rating_refresh import PlayerRatingClass
from models import db, PlayerRating

app = Flask(__name__)
engine_url = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = engine_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')

@app.route('/user', methods=['POST'])
def user_redirect():
    if request.method == 'POST':
        connect_code = request.form['connect_code'].replace("#","-").upper()
        return redirect('/user/' + str(connect_code))

@app.route('/user/<connect_code>', methods=['GET'])
def user(connect_code):
    connect_code = connect_code.replace("-","#").upper()
    
    player_rating_class = PlayerRatingClass(engine_url)
    player_rating_class.insert_new_rating(connect_code)

    player_ratings = PlayerRating.query.where(PlayerRating.connect_code.ilike(connect_code)).order_by(PlayerRating.datetime).all() #.limit(10)
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

if __name__ == '__main__':
    app.run(debug=True)