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

class PlayerSlippiReplay(db.Model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
#    player_id = db.Column(db.Integer, db.ForeignKey('Player.id'), nullable=False)
#    overall_id = db.Column(db.Integer, db.ForeignKey('SlippiOverall.id'))
    slippi_action_counts = db.relationship("SlippiActionCounts", backref='PlayerSlippiReplay', uselist=False)
#    slippi_overall = db.relationship("PlayerSlippiReplay", uselist=False, lazy=True)

class SlippiActionCounts(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
#    slippi_replay = db.Column(db.Integer, db.ForeignKey(PlayerSlippiReplay.id), nullable=False)
#    connect_code = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    replay_id = db.Column(db.Integer, db.ForeignKey('PlayerSlippiReplay.id'))
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
