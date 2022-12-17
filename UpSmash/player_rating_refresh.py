import argparse
import requests
import sqlalchemy as db
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import PlayerRating

class PlayerRatingClass:
    def __init__(self, engine_url):
        self.engine_url = engine_url

    def check_if_rating_is_current(self, connect_code):
        engine = db.create_engine(self.engine_url)
        session = Session(engine)
        player_rating = session.query(PlayerRating).where(PlayerRating.connect_code == connect_code).order_by(PlayerRating.datetime.desc()).first()
        if not player_rating:
            print("New Player")
            return False
        time_30_minutes_ago = datetime.now() - timedelta(minutes=10)
        return player_rating or (player_rating.datetime > time_30_minutes_ago)

    def get_distinct_players(self):
        engine = db.create_engine(self.engine_url)
        session = Session(engine)
        distinct_players = session.query(PlayerRating.connect_code).distinct().all()
        return distinct_players

    def insert_new_rating(self, connect_code): 
        if self.check_if_rating_is_current(connect_code): 
            print("rating is current")
            return False
        connect_code = connect_code.upper()
        rating = self.get_rating(connect_code)

        engine = db.create_engine(self.engine_url)
        connection = engine.connect()
        player_rating = db.Table('player_rating', db.MetaData(), autoload=True, autoload_with=engine)

        if rating:
            new_insert = player_rating.insert().values(connect_code=connect_code, rating=rating, datetime=datetime.now())
            connection.execute(new_insert)

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
        #print(response_json)
        if not str(response.status_code) == "200":
            print("Bad response")
            return False
        if not response_json['data']['getConnectCode']:
            print("No user username: " + connect_code)
            return False
        ranked = response_json["data"]["getConnectCode"]["user"]["rankedNetplayProfile"]
            
        rating = ranked['ratingOrdinal']
        return rating

    def refresh_player_ratings(self):
        distinct_players = self.get_distinct_players()

        for player_connect_code in distinct_players:
            self.insert_new_rating(player_connect_code[0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Handle player rankings')
    parser.add_argument('-r', dest='reload', action='store_true', help='Reload the player ratings')
    parser.add_argument('-n', dest='new_player', help='Add a new player')
    parser.add_argument('-p', dest='players', action='store_true', help='Show distinct players')
    parser.add_argument('-c', dest='distinct_count', action='store_true', help='Show distinct player count')
    args = parser.parse_args()

    engine_url = 'sqlite:///db.sqlite3'
    player_rate = PlayerRatingClass(engine_url)
    if args.reload:
        player_rate.refresh_player_ratings()
    if args.new_player:
        player_rate.insert_new_rating(args.new_player)
    if args.players:
        players = player_rate.get_distinct_players()
        players = list(list(zip(*players))[0])
        print("Players: " + str(players))
    if args.distinct_count:
        print("Total Players: " + str(len(player_rate.get_distinct_players())))
