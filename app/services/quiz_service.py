from app.models import QuizQuestion
import random

def get_random_questions(num_questions=20):
    questions = QuizQuestion.query.all()
    return random.sample(questions, min(num_questions, len(questions)))
