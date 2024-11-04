from flask import render_template, redirect, url_for, flash, session, request
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

@main.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    def get_correct_answer(question_id):
        question = QuizQuestion.query.get(question_id)
        return question.correct_answer if question else None

    # Determine if this is a new quiz or a form submission
    if request.method == 'POST':
        print("This is the POST section of the quiz route")
        user_answers = {}
        
        # Retrieve question IDs from the session
        question_ids = session.get('quiz_questions', [])

        # Debugging: print form data
        print(f"Form data: {request.form}")  # Debug line
        print(f"Session quiz questions during POST: {question_ids}") # Debug line

        # Calculate the score based on submitted answers
        for question_id in question_ids:
            selected_answer = request.form.get(f'answer_{question_id}')
            print(f"Question ID {question_id}, Selected Answer: {selected_answer}")  # Debug line
            user_answers[question_id] = selected_answer or 'None'  # Store user's answer

        score = sum(1 for question_id in question_ids if user_answers[question_id] == get_correct_answer(question_id))  # Use a function to get the correct answer

        # Check if all questions were answered
        if len(user_answers) != len(question_ids):
            flash('Please answer all questions before submitting the quiz.', 'warning')
            return redirect(url_for('main.quiz'))  # Redirect back to quiz if not all answered

        # Save the quiz result to the database
        quiz_result = QuizResult(
            user_id=current_user.id, 
            score=score, 
            user_answers=json.dumps(user_answers),
            question_ids=json.dumps(question_ids)
        )
        db.session.add(quiz_result)
        db.session.commit()

        session.pop('quiz_questions', None)  # Clear session data after processing
        return redirect(url_for('main.results'))  # Redirect to the results page after submission

    # This part handles the GET request and generates new questions
    print("This is the GET section of the quiz route")
    questions = get_random_questions()

    # Store question IDs in session for later reference
    session['quiz_questions'] = [question.id for question in questions]

    # Debugging: print generated question IDs
    print("Generated Questions IDs (GET):", session['quiz_questions'])

    return render_template('quiz.html', questions=questions)

# Results route
@main.route('/results')
@login_required
def results():
    latest_result = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.timestamp.desc()).first()
    if not latest_result:
        flash("No quiz results found.", "warning")
        return redirect(url_for('main.dashboard'))

    user_answers = json.loads(latest_result.user_answers)
    question_ids = json.loads(latest_result.question_ids)

    # Fetch the exact questions that were used in the quiz
    questions = QuizQuestion.query.filter(QuizQuestion.id.in_(question_ids)).all()
    questions_count = len(question_ids)
    
    return render_template(
        'results.html', 
        user=current_user, 
        result=latest_result, 
        questions_count=questions_count, 
        user_answers=user_answers, 
        questions=questions
    )

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
