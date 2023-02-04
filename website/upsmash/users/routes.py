from upsmash.utils import create_new_player, get_player, refresh_player_rating
from flask import render_template, redirect, request, Blueprint, abort
from upsmash.models import PlayerRating, Player, SlippiReplay

users = Blueprint('users', __name__)

def get_safe_connect_code(connect_code):
    return connect_code.replace("#","-").upper()

def get_real_connect_code(connect_code):
    return connect_code.replace("-","#").upper()

def get_or_create_player(connect_code):
    connect_code = get_real_connect_code(connect_code)
    current_player = Player.query.filter_by(connect_code=connect_code).first()
    if not current_player:
        current_player = create_new_player(connect_code)
    return current_player

def get_player_or_abort(connect_code):
    player = get_or_create_player(connect_code)
    if not player:
        abort(404)
    return player
    
@users.route('/user', methods=['POST'])
def user_redirect():
    current_player = get_player_or_abort(request.form['connect_code'])
    return redirect('/user/' + str(get_safe_connect_code(current_player.connect_code)))

@users.route('/user/<connect_code>', methods=['GET'])
def user(connect_code):
    connect_code = get_real_connect_code(connect_code)
    player = get_player_or_abort(connect_code)
    refresh_player_rating(player)
    player = Player.query.filter_by(connect_code=connect_code).first()

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