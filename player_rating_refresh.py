import argparse
import requests
import sqlalchemy as db
import json
from datetime import datetime
from sqlalchemy.orm import Session

class PlayerRatingClass:
    def __init__(self):
        engine = db.create_engine('sqlite:///db.sqlite3')
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Handle player rankings')
    parser.add_argument('-r', dest='reload', action='store_true', help='Reload the player ratings')
    parser.add_argument('-n', dest='new_player', help='Add a new player')
    parser.add_argument('-p', dest='players', action='store_true', help='Show distinct players')
    parser.add_argument('-c', dest='distinct_count', action='store_true', help='Show distinct player count')
    args = parser.parse_args()

    player_rate = PlayerRatingClass()
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
