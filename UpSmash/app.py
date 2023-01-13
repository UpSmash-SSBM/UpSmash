import time
from multiprocessing import Process
import os.path
from datetime import date
from flask import Flask, abort, render_template, url_for, redirect, request
from datetime import datetime, timedelta
from models import db, MeleeCharacters, PlayerRating, Player, SlippiReplay, AllTimePlayerStats, SlippiActionCounts, SlippiOverall
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from operator import itemgetter
import json
import os.path
from sqlalchemy import exc
import requests
import subprocess
#from player_rating_refresh import PlayerRatingClass
from models import MeleeCharacters, PlayerRating, Player, SlippiReplay, SlippiActionCounts, SlippiOverall


def refresh_player_rating(player, rating=None):
    if check_if_player_rating_is_current(player):
        return False
    if not rating:
        rating = get_slippi_rating(player.connect_code)
    player_rating = PlayerRating(player_id=player.id, rating=rating, datetime=datetime.now())
    player.current_rating = rating
    db.session.add(player_rating)
    db.session.commit()

def get_slippi_rating(connect_code):
    return get_slippi_info(connect_code)["rankedNetplayProfile"]['ratingOrdinal']

def calc_ratio(count):
    total = count['success'] + count['fail']
    if total > 0:
        ratio = count['success'] / total
    else:
        ratio = None
    return ratio

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
    #print(response.text)
    try:
        response_json = json.loads(response.text)
    except:
        print(response)
        print(response.text)
        print("Couldn't find player info for: " + connect_code)
        return False
    
    if not str(response.status_code) == "200":
        print("Bad response")
        return False
    if not response_json['data']['getConnectCode']:
        print("No user: " + connect_code)
        return False
    return response_json["data"]["getConnectCode"]["user"]

def create_new_player(connect_code):
    player_info = get_slippi_info(connect_code)
    if not player_info:
        return False
    #print(player_info)
    ranked_info = player_info["rankedNetplayProfile"]
    rating = ranked_info['ratingOrdinal']
    wins = ranked_info['wins']
    losses = ranked_info['losses']
    region = ranked_info['continent']
    username = player_info['displayName']
    char_enum = None
    if len(ranked_info['characters']) > 0:
        character_list = sorted(ranked_info['characters'], key=itemgetter('gameCount'), reverse=True)
        top_character = character_list[0]['character']
        char_enum = MeleeCharacters[top_character]
    current_player = Player(connect_code=connect_code.upper(),username=username, region=region, ranked_wins=wins,ranked_losses=losses)
    if char_enum:
        current_player.character=char_enum
    
    try:
        db.session.add(current_player)
        db.session.commit()
        refresh_player_rating(current_player, rating=rating)
    except exc.IntegrityError:
        db.session.rollback()
    return current_player

def check_if_player_rating_is_current(player):
    player_rating = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime.desc()).first()
    if not player_rating:
        #print("No ratings")
        return False
    time_10_minutes_ago = datetime.now() - timedelta(minutes=10)
    return player_rating.datetime > time_10_minutes_ago

def add_slippi_file_to_overall(slippi_replay, filename, players, overall):
    for player in overall:
        connect_code = players[str(player['playerIndex'])]['names']['code']
        current_player = Player.query.filter_by(connect_code=connect_code).first()
        if not current_player:
            print("Couldn't find player: " + connect_code)
            return False

        new_overall = SlippiOverall(slippi_replay_id=slippi_replay.id, player_id=current_player.id, input_counts=player['inputCounts']['total'], 
            total_damage=player['totalDamage'], kill_count=player['killCount'], successful_conversions=player['successfulConversions']['total'], 
            successful_conversion_ratio=player['successfulConversions']['ratio'], inputs_per_minute=player['inputsPerMinute']['ratio'],digital_inputs_per_minute=player['digitalInputsPerMinute']['ratio'],
            openings_per_kill=player['openingsPerKill']['ratio'], damage_per_opening=player['damagePerOpening']['ratio'], 
            neutral_win_ratio=player['neutralWinRatio']['ratio'], counter_hit_ratio=player['counterHitRatio']['ratio'], 
            beneficial_trades=player['beneficialTradeRatio']['ratio']
        )
        db.session.add(new_overall)
        db.session.commit()

def add_slippi_file_to_action_counts(slippi_replay, filename, players, action_counts):
    for player in action_counts:
        connect_code = players[str(player['playerIndex'])]['names']['code']
        current_player = Player.query.filter_by(connect_code=connect_code).first()
        if not current_player:
            print("Couldn't find player: " + connect_code)
            return False

        lcancel_ratio = calc_ratio(player['lCancelCount'])
        wall_tech_ratio = calc_ratio(player['wallTechCount'])
        
        new_action_count = SlippiActionCounts(slippi_replay_id=slippi_replay.id, player_id=current_player.id, wavedash=player['wavedashCount'], 
            waveland=player['wavelandCount'], airdodge=player['airDodgeCount'], dashdance=player['dashDanceCount'], 
            spotdodge=player['spotDodgeCount'], ledgegrab=player['ledgegrabCount'],roll=player['rollCount'],
            lcancel_success_ratio=lcancel_ratio, grab_success=player['grabCount']['success'], 
            grab_fail=player['grabCount']['fail'], tech_away=player['groundTechCount']['away'], 
            tech_in=player['groundTechCount']['in'], tech=player['groundTechCount']['neutral'],
            tech_fail=player['groundTechCount']['fail'],
            wall_tech_success_ratio=wall_tech_ratio
        )
        db.session.add(new_action_count)
        db.session.commit()

def load_slippi_file(filename):
    json_folder = 'static/json/'
    full_filename = json_folder + filename + '.json'
    if not os.path.exists(full_filename):
        print("Slp file does not exist")
        return False
    with open(full_filename) as f:
        try:
            data = json.load(f)
        except:
            print("Couldn't load file: " + filename)
            return False

        #settings = data['settings']
        stats = data['stats']
        metadata = data['metadata']
        players = metadata['players']
        winner = data['winner']
        winner_id = None

        new_players = []
        #print("PLAYERS: " + str(players))
        for player in players.values():
            if not 'code' in player['names'].keys():
                print("Local game file")
                return False
            connect_code = player['names']['code']
            current_player = Player.query.filter_by(connect_code=connect_code).first()
            if not current_player:
                current_player = create_new_player(connect_code)
                #print("current_player: " + str(current_player))
            current_player = Player.query.filter_by(connect_code=connect_code).first()
            if not current_player:
                print("Couldn't find player: " + connect_code)
                return False
            if connect_code == winner:
                winner_id = current_player.id
            new_players.append(current_player)
        #print("PLAYERS: " + str(new_players))
        if not SlippiReplay.query.filter_by(filename=filename,player1_id=new_players[0].id,player2_id=new_players[1].id).first(): #add test to make sure not already exists
            slippi_datetime = filename[5:20]
            slp_datetime = datetime.strptime(slippi_datetime, '%Y%m%dT%H%M%S')
            #print("slippidatetime: " + slippi_datetime)
            new_slippi_replay = SlippiReplay(filename=filename,player1_id=new_players[0].id,player2_id=new_players[1].id, winner_id=winner_id, datetime=slp_datetime)
            db.session.add(new_slippi_replay)
            db.session.commit()
            #print("replay_id: " + str(new_slippi_replay.id))
            add_slippi_file_to_action_counts(new_slippi_replay, filename, players, stats['actionCounts'])
            add_slippi_file_to_overall(new_slippi_replay, filename, players, stats['overall'])

def load_slippi_files(filename):
    with app.app_context():
        subprocess.run(["node", "../slippi_js/to_json.js",filename])
        slp_path = os.path.join('static/files/', filename)
        os.remove(slp_path)
        base_filename = filename.split('.')[0]
        load_slippi_file(base_filename)
        json_path = os.path.join('static/json/', base_filename + '.json')
        os.remove(json_path)

def refresh_all_ratings():
    with app.app_context():
        while True:
            print("Refreshing all ratings")
            players = Player.query.all()
            for player in players:
                refresh_player_rating(player)
            time.sleep(3600)

def top_50_players_thread():
    with app.app_context():
        while True:
            print("Refreshing top 50 players")
            #players = get_top_50_players()
            with open('player_list.json') as f:
                players = json.load(f)
            #print(players)
            for player in players:
                #print(player)
                connect_code = player[1]
                current_player = Player.query.filter_by(connect_code=connect_code).first()
                if not current_player:
                        current_player = create_new_player(connect_code)
            time.sleep(43200)

def get_top_50_players():
    top_50_players = []

    url = "https://slippi.gg/leaderboards?region="
    regions = ['na', 'eu', 'other']
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    for region in regions:
        driver.get(url + region)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find("table").find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            player_name = cells[2].find("a").get_text()
            player_tag = cells[2].find("p").get_text()
            top_50_players.append((player_name, player_tag))
    driver.close()
    return top_50_players

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
    #print(players_dict)
    return render_template('top_player_graph.html.j2', graph_dates=graph_dates, players_dict=players_dict)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html.j2')

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html.j2')

@app.route('/privacy', methods=['GET'])
def privacy():
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
    app.run(debug=True,host='0.0.0.0')
