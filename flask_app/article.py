from flask_app.db import db


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    annotation = db.Column(db.String(255))
    text = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    compliance_label = db.Column(db.Boolean, nullable=False, default=False)


class BlackList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
