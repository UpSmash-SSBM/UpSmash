from flask import render_template, request, Blueprint
from datetime import date, timedelta
from upsmash.models import PlayerRating, Player
from upsmash.main.utils import upload, games_get, refresh_player_rating
from upsmash.utils import get_player_or_abort

main = Blueprint('main', __name__)

@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html.j2')

@main.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html.j2')

@main.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html.j2')

@main.route('/', methods=['GET'])
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

@main.route('/upload_slp', methods=['POST'])
def upload_slp():
    if request.method == 'POST':
        return upload(request)

@main.route('/top_player_graph', methods=['GET'])
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

@main.route('/rating/<connect_code>', methods=['GET'])
def rating(connect_code):
    player = get_player_or_abort(connect_code)
    refresh_player_rating(player)
    curr_rating = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime).first()
    return curr_rating.toJSON()

@main.route('/player_games/<connect_code>', methods=['GET'])
def get_player_games(connect_code):
    played = games_get(connect_code)
    return played
