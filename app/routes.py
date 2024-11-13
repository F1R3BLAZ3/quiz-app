from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint
from flask import current_app
from app import db, login_manager, csrf
from app.forms import RegistrationForm, LoginForm, QuestionForm
from app.models import User, QuizQuestion, QuizResult
from app.services.quiz_service import get_random_questions
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import json

# Create a blueprint for the routes
main = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by user ID.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user object if found, otherwise None.
    """
    return User.query.get(int(user_id))

# Home route


@main.route('/')
@main.route('/home')
def home():
    """Render the home page.

    Returns:
        str: Rendered HTML for the home page.
    """
    return render_template('home.html')

# Registration route


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration.

    Automatically sets the first registered user as an admin.
    Allows admin users to assign roles to new users.

    Returns:
        str: Rendered HTML for the registration page.
    """
    form = RegistrationForm()
    is_first_user = User.query.first() is None  # Check if this is the first user

    # If this is the first user, set their role to 'admin'
    if is_first_user:
        form.role.data = 'admin'  # Automatically set the role for the first user

    # If not the first user, show the role field only to admins
    elif current_user.is_authenticated and current_user.role == 'admin':
        # Let admins choose between 'admin' and 'user' roles for new users
        form.role.choices = [('user', 'User'), ('admin', 'Admin')]
    else:
        # Set a default role for non-admins creating their own accounts
        form.role.data = 'user'
        # Disable role selection for non-admin users
        form.role.render_kw = {'disabled': 'disabled'}

    if form.validate_on_submit():
        # Check if the username already exists
        existing_user = User.query.filter_by(
            username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.',
                  'danger')
            return render_template('register.html', form=form)

        # Proceed to create the new user
        role = form.role.data if form.role else 'user'
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

# Login route


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    Verifies the username and password, then logs the user in if credentials are correct.

    Returns:
        str: Rendered HTML for the login page.
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve user by username
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Log in the user if credentials are correct
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check username and password.', 'danger')
    return render_template('login.html', form=form)

# Logout route


@main.route('/logout')
@login_required
def logout():
    """Log out the current user.

    Redirects the user to the home page after logging out.

    Returns:
        str: Redirect to the home page after logging out.
    """
    logout_user()
    return redirect(url_for('main.home'))

# Dashboard route


@main.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard.

    Returns:
        str: Rendered HTML for the user dashboard.
    """
    return render_template('dashboard.html', user=current_user)

# Quiz route


@main.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    """Handle the quiz functionality.

    If the request method is POST, user answers are processed and results are saved.
    If GET, a new quiz is generated.

    Returns:
        str: Rendered HTML for the quiz page.
    """
    session['quiz_time_limit'] = current_app.config.get(
        'QUIZ_TIME_LIMIT', 1200)

    def get_correct_answer(question_id):
        """Get the correct answer for a given question ID.

        Args:
            question_id (int): The ID of the question.

        Returns:
            str: The correct answer for the question.
        """
        question = QuizQuestion.query.get(question_id)
        return question.correct_answer if question else None

    if request.method == 'POST':
        is_timeout = request.form.get('timeout') == "1"
        start_time = session.get('quiz_start_time')

        # Check if the quiz time has exceeded the limit
        time_exceeded = time() - start_time > session['quiz_time_limit']
        if not is_timeout and start_time and time_exceeded:
            flash('Your time is up! Submitting the quiz.', 'warning')
            return redirect(url_for('main.results'))

        user_answers = {}
        question_ids = session.get('quiz_questions', [])

        # Collect user answers
        for question_id in question_ids:
            selected_answer = request.form.get(f'answer_{question_id}')
            # Store 'None' if no answer selected
            user_answers[question_id] = selected_answer or 'None'

        # Calculate the score based on correct answers
        correct_answers_count = [
            user_answers[question_id] == get_correct_answer(question_id)
            for question_id in question_ids
        ]
        score = sum(correct_answers_count)

        # Ensure all questions were answered
        if len(user_answers) != len(question_ids):
            flash('Please answer all questions before submitting the quiz.',
                  'warning')
            return redirect(url_for('main.quiz'))

        # Save the quiz result to the database
        quiz_result = QuizResult(
            user_id=current_user.id,
            score=score,
            total_questions=len(question_ids),
            user_answers=json.dumps(user_answers),
            question_ids=json.dumps(question_ids)
        )
        db.session.add(quiz_result)
        db.session.commit()

        # Clear the session data related to the quiz
        session.pop('quiz_questions', None)
        return redirect(url_for('main.results'))

    # Generate a new set of quiz questions
    questions = get_random_questions()
    # Store question IDs in session
    session['quiz_questions'] = [question.id for question in questions]
    session['quiz_start_time'] = time()  # Record the start time for the quiz

    return render_template('quiz.html', questions=questions)

# Results route


@main.route('/results')
@login_required
def results():
    """Display the quiz results for the current user.

    Fetches and displays the most recent quiz result or a result by its ID.

    Returns:
        str: Rendered HTML for the results page.
    """
    result_id = request.args.get("result_id")
    if result_id:
        result = QuizResult.query.filter_by(
            id=result_id, user_id=current_user.id).first()
    else:
        # Get the most recent result for the current user
        result = QuizResult.query.filter_by(user_id=current_user.id).order_by(
            QuizResult.timestamp.desc()).first()

    if not result:
        flash("No quiz results found.", "warning")
        return redirect(url_for('main.dashboard'))

    # Parse user answers from JSON
    user_answers = json.loads(result.user_answers)
    # Parse question IDs from JSON
    question_ids = json.loads(result.question_ids)

    # Fetch the questions attempted in this specific quiz
    questions = QuizQuestion.query.filter(
        QuizQuestion.id.in_(question_ids)).all()

    return render_template('results.html',
                           user=current_user,
                           result=result,
                           questions_count=result.total_questions,
                           user_answers=user_answers,
                           questions=questions)

# Results history route


@main.route('/results_history')
@login_required
def results_history():
    """Display the quiz results history for the current user.

    Returns:
        str: Rendered HTML for the results history page.
    """
    results = QuizResult.query.filter_by(user_id=current_user.id).order_by(
        QuizResult.timestamp.desc()).all()
    return render_template('results_history.html', results=results)

# Add question route


@main.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    """Handle the addition of new quiz questions.

    Ensures the user is an admin before allowing question addition.

    Returns:
        str: Rendered HTML for the add question page.
    """
    # Ensure the user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = QuestionForm()
    if form.validate_on_submit():
        # Create a new quiz question from form data
        question = QuizQuestion(
            question_text=form.question_text.data,
            answer_a=form.answer_a.data,
            answer_b=form.answer_b.data,
            answer_c=form.answer_c.data,
            answer_d=form.answer_d.data,
            correct_answer=form.correct_answer.data
        )
        db.session.add(question)  # Add the question to the session
        db.session.commit()  # Commit the changes to the database
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.add_question'))

    return render_template('add_question.html', form=form)

# View questions route


@main.route('/questions')
@login_required
def view_questions():
    """Allow admins to view all quiz questions.

    Returns:
        str: Rendered HTML to view all quiz questions.
    """
    # Ensure the user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Retrieve all questions from the database
    questions = QuizQuestion.query.all()
    return render_template('view_questions.html', questions=questions)

# Delete question route


@main.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    """Allow admins to delete a quiz question.

    Args:
        question_id (int): The ID of the question to delete.

    Returns:
        str: Redirect to the question view page after deletion.
    """
    # Ensure the user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    question = QuizQuestion.query.get(question_id)
    if question:
        db.session.delete(question)  # Remove the question from the session
        db.session.commit()  # Commit the changes to the database
        flash('Question deleted successfully!', 'success')
    else:
        flash('Question not found.', 'danger')
    return redirect(url_for('main.view_questions'))

# Edit question route


@main.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Allow admins to edit an existing quiz question.

    Args:
        question_id (int): The ID of the question to edit.

    Returns:
        str: Rendered HTML for editing the quiz question.
    """
    # Ensure the user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    question = QuizQuestion.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        # Update the question with form data
        question.question_text = form.question_text.data
        question.answer_a = form.answer_a.data
        question.answer_b = form.answer_b.data
        question.answer_c = form.answer_c.data
        question.answer_d = form.answer_d.data
        question.correct_answer = form.correct_answer.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('main.view_questions'))

    return render_template('edit_question.html', form=form, question=question)
