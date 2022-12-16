from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PlayerRating(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)

class SlippiFile(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    connect_code1 = db.Column(db.String(10), nullable=False)
    connect_code2 = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "SlippiOverall('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(self.filename, self.connect_code, self.input_counts, self.total_damage, self.kill_count, self.successful_conversions, self.successful_conversion_ratio, self.inputs_per_minute, self.digital_inputs_per_minute, self.openings_per_kill, self.damage_per_opening, self.neutral_win_ratio, self.counter_hit_ratio, self.beneficial_trade_ratio, self.datetime)
        
class Player(db.model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(20))

class AllTimePlayerStats(db.models):
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(Integer, ForeignKey(Player.id), nullable=False)

class PlayerSlippiReplay(db.model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    connect_code = db.Column(Integer, ForeignKey(Player.id))
    action_counts = db.Column(Integer, ForeignKey(SlippiActionCounts.id))
    overall = db.Column(Integer, ForeignKey(SlippiOverall.id))

class SlippiActionCounts(db.model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    slippi_replay = db.Column(Integer, ForeignKey(PlayerSlippiReplay.id), nullable=False)
    connect_code = db.Column(Integer, ForeignKey(Player.id), nullable=False)
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
    datetime = db.Column(db.DateTime)

    def __repr__(self):
        return "SlippiActionCount({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(self.filename, self.connect_code, self.wavedash, self.waveland, self.airdodge, self.dashdance, self.spotdodge, self.ledgegrab, self.roll, self.lcancel_success_ratio, self.grab_success, self.grab_fail, self.tech_away, self.tech_in, self.tech, self.tech_fail, self.wall_tech_success_ratio, self.datetime)

class SlippiOverall(db.model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    slippi_replay = db.Column(Integer, ForeignKey(PlayerSlippiReplay.id), nullable=False)
    connect_code = db.Column(Integer, ForeignKey(Player.id), nullable=False)
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
    beneficial_trade_ratio = db.Column(db.Float)
    datetime = db.Column(db.DateTime)

    def __repr__(self):
        return "Slippi('{}','{}')".format(self.filename, self.lcancel)
