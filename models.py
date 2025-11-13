from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# -------------------- User Model --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # Relationship to documents
    documents = db.relationship('Document', backref='user', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

# -------------------- Document Model --------------------
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    summary = db.Column(db.Text)

    # Automatically stores when a document is uploaded
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.filename} uploaded at {self.upload_date}>"

# -------------------- Quiz Results Model --------------------
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    score = db.Column(db.Integer)             # number of correct answers
    total = db.Column(db.Integer)             # total questions
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QuizResult User:{self.user_id} Score:{self.score}/{self.total}>"
