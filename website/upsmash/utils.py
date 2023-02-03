from operator import itemgetter
import requests
import json
from sqlalchemy import exc
from datetime import datetime, timedelta
from upsmash import db
from upsmash.models import PlayerRating, Player, MeleeCharacters

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

def get_slippi_rating(connect_code):
    return get_slippi_info(connect_code)["rankedNetplayProfile"]['ratingOrdinal']

def check_if_player_rating_is_current(player):
    player_rating = PlayerRating.query.filter_by(player_id=player.id).order_by(PlayerRating.datetime.desc()).first()
    if not player_rating:
        #print("No ratings")
        return False
    time_10_minutes_ago = datetime.now() - timedelta(minutes=10)
    return player_rating.datetime > time_10_minutes_ago

def refresh_player_rating(player, rating=None):
    if check_if_player_rating_is_current(player):
        return False
    if not rating:
        rating = get_slippi_rating(player.connect_code)
    player_rating = PlayerRating(player_id=player.id, rating=rating, datetime=datetime.now())
    player.current_rating = rating
    db.session.add(player_rating)
    db.session.commit()

def get_player(player_id):
    current_player = Player.query.filter_by(id=player_id).first()
    if current_player:
        return current_player.id
    else:
        print("Couldn't find player")
        return None

def create_new_player(connect_code):
    player_info = get_slippi_info(connect_code)
    if not player_info:
        print("Couldn't find slippi player")
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