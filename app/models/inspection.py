from app.extensions import db

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    damage_report = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    status = db.Column(db.Enum("pending", "reviewed", "completed"), default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    inspected_by = db.Column(db.Integer, db.ForeignKey("user.id"))