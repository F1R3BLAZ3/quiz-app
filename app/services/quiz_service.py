from app.models import QuizQuestion
import random


def get_random_questions(num_questions=20):
    """
    Fetches a random subset of quiz questions from the database.

    Args:
        num_questions (int): The number of questions to retrieve.
        Defaults to 20.

    Returns:
        list: A list of randomly selected QuizQuestion objects.
    """
    # Fetch all questions from the database
    questions = QuizQuestion.query.all()

    # Select a random sample of questions, limited by the smaller of
    # num_questions or total questions
    return random.sample(questions, min(num_questions, len(questions)))
