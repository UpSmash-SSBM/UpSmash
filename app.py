from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
import argparse
import sqlalchemy as db
from sqlalchemy.orm import Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)

class PlayerRatingClass:
    def __init__(self):
        engine = db.create_engine('sqlite:///db.sqlite3',{})
        connection = engine.connect()
        metadata = db.MetaData()
        player_rating = db.Table('player_rating', metadata, autoload=True, autoload_with=engine)

        self.engine = engine
        self.connection = connection
        self.player_rating = player_rating

    def get_distinct_players(self):
        player_rating_query = db.select([self.player_rating])
        player_ratings = self.connection.execute(player_rating_query).fetchall()
        session = Session(self.engine)
        distinct_players = session.query(PlayerRating.connect_code).distinct().all()
        return distinct_players

    def insert_new_rating(self, connect_code): 
        connect_code = connect_code.upper()
        rating = self.get_rating(connect_code)
        if rating:
            new_insert = self.player_rating.insert().values(connect_code=connect_code, rating=rating, datetime=datetime.now())
            self.connection.execute(new_insert)

    def get_rating(self, connect_code):
        connect_code = connect_code.upper()
        url = "https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql"
        connection_object = {
            "operationName": "AccountManagementPageQuery",
            "query": "fragment userProfilePage on User {\n  fbUid\n  displayName\n  connectCode {\n    code\n    __typename\n  }\n  status\n  activeSubscription {\n    level\n    hasGiftSub\n    __typename\n  }\n  rankedNetplayProfile {\n    id\n    ratingOrdinal\n    ratingUpdateCount\n    wins\n    losses\n    dailyGlobalPlacement\n    dailyRegionalPlacement\n    continent\n    characters {\n      id\n      character\n      gameCount\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery AccountManagementPageQuery($cc: String!, $uid: String!) {\n  getUser(fbUid: $uid) {\n    ...userProfilePage\n    __typename\n  }\n  getConnectCode(code: $cc) {\n    user {\n      ...userProfilePage\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {"cc": connect_code, "uid": connect_code},
            "cc":connect_code,
            "uid":connect_code
        }
        response = requests.post(url, json = connection_object)
        response_json = json.loads(response.text)
        if response.status_code != "200":
            return False
        if not response_json['data']['getUser']:
            print("No user user username: " + connect_code)
            return False
        ranked = response_json["data"]["getConnectCode"]["user"]["rankedNetplayProfile"]
            
        rating = ranked['ratingOrdinal']
        return rating

    def refresh_player_ratings(self):
        distinct_players = self.get_distinct_players()

        for player_connect_code in distinct_players:
            self.insert_new_rating(player_connect_code[0])

class TextInputForm(FlaskForm):
    connect_code = StringField("connect_code", validators=[InputRequired()], render_kw={"placeholder": "Enter player Slippi tag"})
    submit = SubmitField("Go")

class PlayerRating(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)

@app.route('/', methods=['GET'])
def index():
    player_search_form = TextInputForm()
    if player_search_form.validate_on_submit():
        return redirect('/')
    player_ratings = PlayerRating.query.order_by(PlayerRating.datetime).all()
    return render_template('index.html', player_ratings=player_ratings, player_search_form=player_search_form)

@app.route('/user', methods=['POST'])
def user_redirect():
    player_search_form = TextInputForm()
    if player_search_form.validate_on_submit():
        connect_code = player_search_form.connect_code.data.replace("#","-").upper()
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