from upsmash.models import Player
from upsmash import create_min_app
from upsmash.utils import create_new_player
from flask import abort

app = create_min_app()
app.app_context().push()

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