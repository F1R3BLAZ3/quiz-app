from app import db
from flask_login import UserMixin
import json


class User(db.Model, UserMixin):
    """User model for storing user account information.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username for the user.
        password (str): The hashed password for the user.
        quiz_results (list): The quiz results associated with the user.
        role (str): The role of the user (either 'user' or 'admin').
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)
    role = db.Column(db.String(50), nullable=False, default='user')

    @property
    def is_admin(self):
        """Check if the user has admin privileges."""
        return self.role == 'admin'


class QuizQuestion(db.Model):
    """QuizQuestion model for storing quiz questions and answers.

    Attributes:
        id (int): The primary key for the quiz question.
        question_text (str): The text of the quiz question.
        answer_a (str): The text of answer A.
        answer_b (str): The text of answer B.
        answer_c (str): The text of answer C.
        answer_d (str): The text of answer D.
        correct_answer (str): The correct answer identifier (A, B, C, or D).
    """
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    answer_a = db.Column(db.String(100), nullable=False)
    answer_b = db.Column(db.String(100), nullable=False)
    answer_c = db.Column(db.String(100), nullable=False)
    answer_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

    @property
    def options(self):
        """Returns a list of answer options for the quiz question.

        Returns:
            list: A list of dictionaries containing answer identifiers
                  and their texts.
        """
        return [
            {"id": "A", "text": self.answer_a},
            {"id": "B", "text": self.answer_b},
            {"id": "C", "text": self.answer_c},
            {"id": "D", "text": self.answer_d},
        ]

    @property
    def correct_answer_text(self):
        """Returns the text of the correct answer.

        Returns:
            str: The text of the correct answer or 'Unknown' if not found.
        """
        options_dict = {option['id']: option['text']
                        for option in self.options}
        return options_dict.get(self.correct_answer, 'Unknown')

    def user_answer_text(self, user_answer):
        """Returns the text of the user's answer.

        Args:
            user_answer (str): The user's selected answer identifier.

        Returns:
            str: The text of the user's answer or
                 'No answer provided' if not found.
        """
        options_dict = {option['id']: option['text']
                        for option in self.options}
        return options_dict.get(user_answer, 'No answer provided')


class QuizResult(db.Model):
    """QuizResult model for storing the results of user quizzes.

    Attributes:
        id (int): The primary key for the quiz result.
        user_id (int): The foreign key referencing the user.
        score (int): The score achieved by the user.
        timestamp (datetime): The timestamp when the quiz was taken.
        total_questions (int): The total number of questions in the quiz.
        user_answers (list): A list of the user's answers as a JSON array.
        question_ids (list): A list of the question IDs as a JSON array.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_questions = db.Column(db.Integer)
    user_answers = db.Column(db.JSON, nullable=False, default=json.dumps([]))
    question_ids = db.Column(db.JSON, nullable=False, default=json.dumps([]))
