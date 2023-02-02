from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class MeleeCharacters(enum.Enum):
    CAPTAIN_FALCON = 0
    DONKEY_KONG = 1
    FOX = 2
    GAME_AND_WATCH = 3
    KIRBY = 4
    BOWSER = 5
    LINK = 6
    LUIGI = 7
    MARIO = 8
    MARTH = 9
    MEWTWO = 10
    NESS = 11
    PEACH = 12
    PIKACHU = 13
    ICE_CLIMBERS = 14
    JIGGLYPUFF = 15
    SAMUS = 16
    YOSHI = 17
    ZELDA = 18
    SHEIK = 19
    FALCO = 20
    YOUNG_LINK = 21
    DR_MARIO = 22
    ROY = 23
    PICHU = 24
    GANONDORF = 25

    def __str__(self):
        return self.name

class PlayerRating(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player = db.relationship("Player", backref=db.backref("player_rating", uselist=False))
    datetime = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)
    
    def __str__(self):
        return f'{self.id},{self.rating},{self.datetime}'

    def toJSON(self):
        rating_dict = {
            "id": self.id,
            "rating": self.rating,
            "datetime": self.datetime
        }
        return rating_dict

class Player(db.Model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(10), nullable=False, unique=True)
    username = db.Column(db.String(20))
    character = db.Column(db.Enum(MeleeCharacters))
    region = db.Column(db.String(40))
    current_rating = db.Column(db.Float)
    ranked_wins = db.Column(db.Integer)
    ranked_losses = db.Column(db.Integer)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)

class SlippiReplay(db.Model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player1 = db.relationship("Player", foreign_keys=[player1_id], backref=db.backref("player1_replay", uselist=False))
    player2_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player2 = db.relationship("Player", foreign_keys=[player2_id], backref=db.backref("player2_replay", uselist=False))
    winner_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    winner = db.relationship("Player", foreign_keys=[winner_id], backref=db.backref("winner_replay", uselist=False))
    datetime = db.Column(db.DateTime)

    def get_player(self, player_id):
        current_player = Player.query.filter_by(id=player_id).first()
        return current_player.connect_code

    def get_overall(self, player_number):
        if player_number == 1:
            overall = SlippiOverall.query.filter_by(slippi_replay_id=self.id,player_id=self.player1_id).first()
        elif player_number == 2:
            overall = SlippiOverall.query.filter_by(slippi_replay_id=self.id,player_id=self.player2_id).first()
        return overall

    def get_player_overall_ordered(self, id):

        player1 = self.get_overall(1)
        player2 = self.get_overall(2)

        if player1.player_id == id:
            return [player1, player2]
        else:
            return [player2, player1]

    def get_action_count(self, player_number):
        if player_number == 1:
            current_player = Player.query.filter_by(id=self.player1_id).first()
        elif player_number == 2:
            current_player = Player.query.filter_by(id=self.player2_id).first()
        return current_player.connect_code

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)

class AllTimePlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player = db.relationship("Player", backref=db.backref("player_all_time_stats", uselist=False))
    games_played = db.Column(db.Integer)
    games_won = db.Column(db.Integer)
    max_elo = db.Column(db.Integer)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)

class SlippiActionCounts(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    slippi_replay_id = db.Column(db.Integer, db.ForeignKey("slippi_replay.id"), nullable=False)
    slippi_replay = db.relationship("SlippiReplay", backref=db.backref("slippi_replay_action_count", uselist=False))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player = db.relationship("Player", backref=db.backref("player_action_count", uselist=False))
    wavedash = db.Column(db.Integer)
    waveland = db.Column(db.Integer)
    airdodge = db.Column(db.Integer)
    dashdance = db.Column(db.Integer)
    spotdodge = db.Column(db.Integer)
    ledgegrab = db.Column(db.Integer)
    roll = db.Column(db.Integer)
    lcancel_success_ratio = db.Column(db.Float)
    grab_success = db.Column(db.Integer)
    grab_fail = db.Column(db.Integer)
    tech_away = db.Column(db.Integer)
    tech_in = db.Column(db.Integer)
    tech = db.Column(db.Integer)
    tech_fail = db.Column(db.Integer)
    wall_tech_success_ratio = db.Column(db.Float)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)

class SlippiOverall(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    slippi_replay_id = db.Column(db.Integer, db.ForeignKey("slippi_replay.id"), nullable=False)
    slippi_replay = db.relationship("SlippiReplay", backref=db.backref("slippi_replay_overall", uselist=False))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player = db.relationship("Player", backref=db.backref("player_overall", uselist=False))
    input_counts = db.Column(db.Integer)
    total_damage = db.Column(db.Float)
    kill_count = db.Column(db.Integer)
    successful_conversions = db.Column(db.Integer)
    successful_conversion_ratio = db.Column(db.Float)
    inputs_per_minute = db.Column(db.Float)
    digital_inputs_per_minute = db.Column(db.Float)
    openings_per_kill = db.Column(db.Float)
    damage_per_opening = db.Column(db.Float)
    neutral_win_ratio = db.Column(db.Float)
    counter_hit_ratio = db.Column(db.Float)
    beneficial_trades = db.Column(db.Float)
    most_common_kill_move = db.Column(db.Integer)
    most_common_neutral_openings = db.Column(db.Integer)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)