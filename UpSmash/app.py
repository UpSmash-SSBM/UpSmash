import time
from multiprocessing import Process
import os.path
from datetime import date
from flask import Flask, abort, render_template, url_for, redirect, request
from datetime import datetime, timedelta
from models import db, MeleeCharacters, PlayerRating, Player, SlippiReplay, AllTimePlayerStats, SlippiActionCounts, SlippiOverall
from flask_dropzone import Dropzone
from app_methods import *

app = Flask(__name__)
engine_url = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = engine_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
db.init_app(app)
dropzone = Dropzone(app)

if not os.path.exists('db.sqlite3'):
    print("Creating new database")
    with app.app_context():
        db.create_all()

@app.before_first_request
def check_refresh_timings():
    proc = Process(target=top_50_players_thread)
    proc.start()
    proc = Process(target=refresh_all_ratings)
    proc.start()

@app.route('/', methods=['GET'])
def index():
    check_refresh_timings()
    na_players = Player.query.filter_by(region='NORTH_AMERICA').order_by(Player.current_rating.desc()).limit(10)
    eu_players = Player.query.filter_by(region='EUROPE').order_by(Player.current_rating.desc()).limit(10)
    other_players = Player.query.filter(Player.region != 'NORTH_AMERICA', Player.region != 'EUROPE').order_by(Player.current_rating.desc()).limit(10)

    context = {
        "na_players": list(na_players),
        "eu_players": list(eu_players),
        "other_players": list(other_players),
    }
    return render_template('index.html.j2', **context)

@app.route('/top_player_graph', methods=['GET'])
def top_player_graph():
    check_refresh_timings()
    tomorrow = date.today() + timedelta(days=1)
    dates = {}
    for i in range(7):
        start_date = tomorrow - timedelta(days=(i+1))
        end_date = tomorrow - timedelta(days=i)
        dates[start_date] = []
        top_10_ratings = PlayerRating.query.with_entities(PlayerRating.player_id, PlayerRating.rating).filter(PlayerRating.datetime <= end_date).filter(PlayerRating.datetime >= start_date).order_by(PlayerRating.rating.desc()).limit(10).distinct()
        for rating in top_10_ratings:
            player = Player.query.filter_by(id=rating.player_id).first()
            new_player_rating = {
                "player": player.username,
                "rating": rating.rating
            }
            dates[start_date].append(new_player_rating)
    graph_dates = []
    for date_key in dates.keys():
        graph_dates.append(date_key.strftime("%Y-%m-%d"))

    players = []
    players_dict = {}
    for rating_date in dates.values():
        for rating in rating_date:
            if not rating['player'] in players:
                players.append(rating['player'])
            if not rating['player'] in players_dict.keys():
                players_dict[rating['player']] = []   
    #print(dates) 
    for player in players:
        for rating_date, player_ratings in dates.items():
            player_rating = "N/A"
            #print(player_ratings)
            for rating in player_ratings:
                if rating['player'] == player:
                    player_rating = rating['rating']
                    break
            players_dict[player].append(player_rating)
    print(players_dict)
    return render_template('top_player_graph.html.j2', graph_dates=graph_dates, players_dict=players_dict)

@app.route('/about', methods=['GET'])
def about():
    check_refresh_timings()
    return render_template('about.html.j2')

@app.route('/faq', methods=['GET'])
def faq():
    check_refresh_timings()
    return render_template('faq.html.j2')

@app.route('/privacy', methods=['GET'])
def privacy():
    check_refresh_timings()
    return render_template('privacy.html.j2')

@app.route('/upload_slp', methods=['POST'])
def upload_slp():
    if request.method == 'POST':
        files = request.files
        #print("Number of files: " + str(len(files.keys())))
        start_time = time.time()
        for new_file in files.values():
            filename = new_file.filename
            new_file.save(os.path.join('static/files/', filename))
            #load_slippi_files(filename)
            proc = Process(target=load_slippi_files, args=(filename,))
            proc.start()
        #print("--- %s seconds ---" % (time.time() - start_time))
        #print(f.filename)
    return 'upload template'

@app.route('/user', methods=['POST'])
def user_redirect():
    connect_code = request.form['connect_code'].replace("-","#").upper()
    current_player = Player.query.filter_by(connect_code=connect_code).first()
    if not current_player:
        current_player = create_new_player(connect_code)
    if not current_player:
        abort(404)
    return redirect('/user/' + str(current_player.id))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html.j2'), 404

@app.route('/user/<player_id>', methods=['GET'])
def user(player_id):
    check_refresh_timings()
    if '-' in player_id: #is a tag
        possible_connect_code = player_id.replace("-","#").upper()
        current_player = Player.query.filter_by(connect_code=possible_connect_code).first()
        if not current_player: #if no player exists, try to create 
            current_player = create_new_player(possible_connect_code)
        if current_player:
            player_id = current_player.id
    player = Player.query.get_or_404(player_id)
    refresh_player_rating(player)
    player = Player.query.get_or_404(player_id)

    player_ratings = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime).all() #.limit(10)
    data_items = []
    for rating in player_ratings:
        data_items.append([rating.datetime.strftime("%Y-%m-%dT%H:%M:%S"), int(rating.rating)])

    character_image_location = 'images/stock_icons/' + str(player.character).lower() + '.png'
    
    total_games = SlippiReplay.query.filter((SlippiReplay.player1_id==player.id) | (SlippiReplay.player2_id==player.id)).count()
    wins = SlippiReplay.query.filter_by(winner_id=player.id).count()
    losses = total_games - wins
    slippi_replays = SlippiReplay.query.filter((SlippiReplay.player1_id==player.id) | (SlippiReplay.player2_id==player.id)).order_by(SlippiReplay.datetime).limit(20)
    context = {
        "player_ratings": player_ratings,
        "player": player,
        "character_image_location": character_image_location,
        "data_items": data_items,
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "slippi_replays": list(slippi_replays),
    }
    return render_template('user.html.j2', **context)

if __name__ == '__main__':
    app.run(debug=True)