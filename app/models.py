from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    answer_a = db.Column(db.String(100), nullable=False)
    answer_b = db.Column(db.String(100), nullable=False)
    answer_c = db.Column(db.String(100), nullable=False)
    answer_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

    @property
    def options(self):
        return [
            {"id": "A", "text": self.answer_a},
            {"id": "B", "text": self.answer_b},
            {"id": "C", "text": self.answer_c},
            {"id": "D", "text": self.answer_d},
        ]

    @property
    def correct_answer_text(self):
        options_dict = {option['id']: option['text'] for option in self.options}
        return options_dict.get(self.correct_answer, 'Unknown')
    
    def user_answer_text(self, user_answer):
        options_dict = {option['id']: option['text'] for option in self.options}
        return options_dict.get(user_answer, 'No answer provided')


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_answers = db.Column(db.JSON, nullable=False)
