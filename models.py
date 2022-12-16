
class PlayerRating(db.Model):
    """A slippi action counts"""
    id = db.Column(db.Integer, primary_key=True)
    connect_code = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)
