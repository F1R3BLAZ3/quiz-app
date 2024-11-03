from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager, csrf
from app.forms import RegistrationForm, LoginForm, QuestionForm
from app.models import User, QuizQuestion, QuizResult
from app.services.quiz_service import get_random_questions
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
import json

# Create a blueprint for the routes
main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')

# Registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('main.login'))  # Use 'main.login' to refer to the blueprint
    return render_template('register.html', form=form)

# Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))  # Use 'main.dashboard' to refer to the blueprint
        else:
            flash('Login failed. Check username and password.', 'danger')
    return render_template('login.html', form=form)

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))  # Use 'main.home' to refer to the blueprint

# Dashboard route
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Quiz route
@main.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    questions = get_random_questions()
    score = 0  # Initialize score outside of the form validation check

    if request.method == 'POST':
        user_answers = {}
        print("Form submitted.")
        for question in questions:
            selected_answer = request.form.get(f'answer_{question.id}')
            user_answers[question.id] = selected_answer or 'None'  # Store user's answer

            if selected_answer and selected_answer == question.correct_answer:
                score += 1  # Increment score for each correct answer

        # Save the quiz result to the database
        quiz_result = QuizResult(user_id=current_user.id, score=score, user_answers=json.dumps(user_answers))  # Store user answers as JSON
        db.session.add(quiz_result)
        db.session.commit()

        flash(f'You scored {score} out of {len(questions)}', 'success')
        return redirect(url_for('main.results'))  # Redirect to the results page after submission

    return render_template('quiz.html', questions=questions)


# Results route
@main.route('/results')
@login_required
def results():
    questions_count = len(get_random_questions())
    latest_result = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.timestamp.desc()).first()

    user_answers = json.loads(latest_result.user_answers) if latest_result else {}

    # Fetch the questions for feedback
    questions = QuizQuestion.query.filter(QuizQuestion.id.in_(user_answers.keys())).all()
    
    return render_template('results.html', user=current_user, result=latest_result, questions_count=questions_count, user_answers=user_answers, questions=questions)

# Question adding route
@main.route('/add_question', methods=['GET', 'POST'])
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = QuizQuestion(
            question_text=form.question_text.data,
            answer_a=form.answer_a.data,
            answer_b=form.answer_b.data,
            answer_c=form.answer_c.data,
            answer_d=form.answer_d.data,
            correct_answer=form.correct_answer.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.add_question'))  # Redirect to the same page after submission

    return render_template('add_question.html', form=form)

# Register the blueprint in the application factory
def register_routes(app):
    app.register_blueprint(main)
