from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question', validators=[DataRequired()])
    answer_a = StringField('Answer A', validators=[DataRequired()])
    answer_b = StringField('Answer B', validators=[DataRequired()])
    answer_c = StringField('Answer C', validators=[DataRequired()])
    answer_d = StringField('Answer D', validators=[DataRequired()])
    correct_answer = SelectField('Correct Answer', choices=[
        ('A', 'Answer A'),
        ('B', 'Answer B'),
        ('C', 'Answer C'),
        ('D', 'Answer D')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Question')
