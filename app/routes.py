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
        # Check if the username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)

        # Proceed to create the new user
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('main.login'))  
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
            return redirect(url_for('main.dashboard'))  
        else:
            flash('Login failed. Check username and password.', 'danger')
    return render_template('login.html', form=form)

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# Dashboard route
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Quiz route
@main.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    session['quiz_time_limit'] = current_app.config.get('QUIZ_TIME_LIMIT', 1200)

    def get_correct_answer(question_id):
        question = QuizQuestion.query.get(question_id)
        return question.correct_answer if question else None

    if request.method == 'POST':
        is_timeout = request.form.get('timeout') == "1"
        start_time = session.get('quiz_start_time')
        if not is_timeout and start_time and (time() - start_time > session['quiz_time_limit']):
            flash('Your time is up! Submitting the quiz.', 'warning')
            return redirect(url_for('main.results'))
        
        user_answers = {}
        question_ids = session.get('quiz_questions', [])

        for question_id in question_ids:
            selected_answer = request.form.get(f'answer_{question_id}')
            user_answers[question_id] = selected_answer or 'None'  

        score = sum(1 for question_id in question_ids if user_answers[question_id] == get_correct_answer(question_id))

        if len(user_answers) != len(question_ids):
            flash('Please answer all questions before submitting the quiz.', 'warning')
            return redirect(url_for('main.quiz'))  

        quiz_result = QuizResult(
            user_id=current_user.id,
            score=score,
            total_questions=len(question_ids),
            user_answers=json.dumps(user_answers),
            question_ids=json.dumps(question_ids)
        )
        db.session.add(quiz_result)
        db.session.commit()

        session.pop('quiz_questions', None)  
        return redirect(url_for('main.results'))  

    questions = get_random_questions()
    session['quiz_questions'] = [question.id for question in questions]
    session['quiz_start_time'] = time()  

    return render_template('quiz.html', questions=questions)

@main.route('/results')
@login_required
def results():
    result_id = request.args.get("result_id")
    if result_id:
        result = QuizResult.query.filter_by(id=result_id, user_id=current_user.id).first()
    else:
        result = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.timestamp.desc()).first()

    if not result:
        flash("No quiz results found.", "warning")
        return redirect(url_for('main.dashboard'))

    user_answers = json.loads(result.user_answers)
    question_ids = json.loads(result.question_ids)

    # Fetch the questions attempted in this specific quiz
    questions = QuizQuestion.query.filter(QuizQuestion.id.in_(question_ids)).all()

    return render_template(
        'results.html',
        user=current_user,
        result=result,
        questions_count=result.total_questions,
        user_answers=user_answers,
        questions=questions
    )

# Results history route
@main.route('/results_history')
@login_required
def results_history():
    results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.timestamp.desc()).all()
    return render_template('results_history.html', results=results)

# Add question route
@main.route('/add_question', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('main.add_question'))  

    return render_template('add_question.html', form=form)

# Display question route
@main.route('/questions', methods=['GET'])
@login_required
def view_questions():
    questions = QuizQuestion.query.all()
    return render_template('view_questions.html', questions=questions)

# Delete question route
@main.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully.', 'success')
    return redirect(url_for('main.view_questions'))

# Edit question route
@main.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('main.view_questions'))  

    return render_template('edit_question.html', form=form, question=question)

def register_routes(app):
    app.register_blueprint(main)
