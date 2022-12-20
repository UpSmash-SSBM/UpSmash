from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import json
import argparse
#from player_rating_refresh import PlayerRatingClass
from models import db, PlayerRating, Player, MeleeCharacters
from operator import itemgetter
import os.path

app = Flask(__name__)
engine_url = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = engine_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
db.init_app(app)

if not os.path.exists('db.sqlite3'):
    print("Creating new database")
    with app.app_context():
        db.create_all()

def get_slippi_rating(connect_code):
    return get_slippi_info(connect_code)["rankedNetplayProfile"]['ratingOrdinal']

def get_slippi_info(connect_code):
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
    if not str(response.status_code) == "200":
        print("Bad response")
        return False
    if not response_json['data']['getConnectCode']:
        print("No user username: " + connect_code)
        return False
    return response_json["data"]["getConnectCode"]["user"]

def create_new_player(connect_code):
    player_info = get_slippi_info(connect_code)
    if not player_info:
        return False
    ranked_info = player_info["rankedNetplayProfile"]
    username = player_info['displayName']
    character_list = sorted(ranked_info['characters'], key=itemgetter('gameCount'), reverse=True)
    top_character = character_list[0]['character']
    char_enum = MeleeCharacters[top_character]
    current_player = Player(connect_code=connect_code.upper(),username=username,character=char_enum)
    db.session.add(current_player)
    db.session.commit()
    return current_player

def check_if_player_rating_is_current(player):
    player_rating = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime.desc()).first()
    if not player_rating:
        print("No ratings")
        return False
    time_30_minutes_ago = datetime.now() - timedelta(minutes=10)
    return player_rating.datetime > time_30_minutes_ago

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
    connect_code = request.form['connect_code']
    current_player = Player.query.filter_by(connect_code=connect_code).first()
    if not current_player:
        current_player = create_new_player(connect_code)
    return redirect('/user/' + str(current_player.id))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/user/<player_id>', methods=['GET'])
def user(player_id):
    if '-' in player_id: #is a tag
        possible_connect_code = player_id.replace("-","#").upper()
        current_player = Player.query.filter_by(connect_code=possible_connect_code).first()
        if not current_player: #if no player exists, try to create 
            current_player = create_new_player(possible_connect_code)
        if current_player:
            player_id = current_player.id
    player = Player.query.get_or_404(player_id)
    #player_rating_class = PlayerRatingClass(engine_url)
    #ranked_info = player_rating_class.insert_new_rating(connect_code)
    if not check_if_player_rating_is_current(player):
        rating = get_slippi_rating(player.connect_code)
        new_rating = PlayerRating(player_id=player.id, rating=rating, datetime=datetime.now())
        db.session.add(new_rating)
        db.session.commit()

    player_ratings = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime).all() #.limit(10)
    datetimes = []
    ratings = []
    for rating in player_ratings:
        datetimes.append(rating.datetime.strftime("%m/%d/%Y, %H:%M:%S"))
        ratings.append(rating.rating)
    character_image_location = 'images/stock_icons/' + str(player.character).lower() + '.png'
    context = {
        "player_ratings": player_ratings,
        "username": player.username,
        "character_image_location": character_image_location,
        "datetimes": datetimes,
        "ratings": ratings
    }
    return render_template('user.html', **context)

if __name__ == '__main__':
    app.run(debug=True)