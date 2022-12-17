class Player(db.Model):
    """A slippi replay"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(20))
    player = db.relationship("PlayerSlippiReplay", uselist=False, lazy=True)


class AllTimePlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)

class SlippiOverall(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
#    slippi_replay = db.Column(db.Integer, db.ForeignKey(PlayerSlippiReplay.id), nullable=False)
#    connect_code = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
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