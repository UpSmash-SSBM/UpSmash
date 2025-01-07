from upsmash.utils import refresh_player_rating
from flask import render_template, redirect, request, Blueprint
from upsmash.models import PlayerRating, Player, SlippiReplay, MatchType
from upsmash.utils import get_player_or_abort, get_safe_connect_code, get_real_connect_code
from upsmash.users.utils import get_rank_icon, get_rank

users = Blueprint('users', __name__)

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
    print(player.ranked_wins)

    player_ratings = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime).all() #.limit(10)
    data_items = []
    for rating in player_ratings:
        data_items.append([rating.datetime, int(rating.rating)])
    
    total_games = SlippiReplay.query.filter((SlippiReplay.player1_id==player.id) | (SlippiReplay.player2_id==player.id)).count()
    unranked_wins = SlippiReplay.query.filter_by(winner_id=player.id).filter_by(game_type=MatchType.UNRANKED).count()
    total_unranked_games = SlippiReplay.query.filter((SlippiReplay.player1_id==player.id) | (SlippiReplay.player2_id==player.id)).filter_by(game_type=MatchType.UNRANKED).count()
    unranked_losses = total_unranked_games - unranked_wins
    slippi_replays = SlippiReplay.query.filter((SlippiReplay.player1_id==player.id) | (SlippiReplay.player2_id==player.id)).order_by(SlippiReplay.datetime.desc())
    
    games = [
        {
            'name': 'ranked',
            'games': slippi_replays.filter_by(game_type='RANKED').limit(40)
        },
        {
            'name': 'unranked',
            'games': slippi_replays.filter_by(game_type='UNRANKED').limit(40)
        },
        {
            'name': 'direct',
            'games': slippi_replays.filter_by(game_type='DIRECT').limit(40)
        },
        {
            'name': 'other',
            'games': slippi_replays.filter(SlippiReplay.game_type==None).limit(40)
        },
    ]
    #print(list(games[3]['games']))
    context = {
        "player_ratings": player_ratings,
        "player": player,
        "character_image_location": 'images/stock_icons/' + str(player.character).lower() + '.png',
        "rank_icon_location": get_rank_icon(player.current_rating),
        "rank": get_rank(player.current_rating),
        "data_items": data_items,
        "total_games": total_games,
        "wins": unranked_wins,
        "losses": unranked_losses,
        "games": games,
        "slippi_replays": list(slippi_replays),
    }
    return render_template('user.html.j2', **context)