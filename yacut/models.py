from datetime import datetime, timezone

from yacut import db


class URLMap(db.Model):
    __tablename__ = "url_map"

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<URLMap short={self.short} original={self.original[:60]}>"

    def to_dict(self):
        return {"url": self.original, "short_link": self.short}
