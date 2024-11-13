from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length


class RegistrationForm(FlaskForm):
    """Form for user registration.

    This form captures the necessary information for user registration,
    including fields for the username, password, and role selection.

    Attributes:
        username (StringField): The username field, requires a 3-20 character length.
        password (PasswordField): The password field, with a minimum length of 6 characters.
        password2 (PasswordField): The field for confirming the password, validated against 'password'.
        role (SelectField): The role selection field with options for 'User' or 'Admin'.
        submit (SubmitField): The submission button.
    """
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=3, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=6)])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    role = SelectField('Role',
                       choices=[('user', 'User'),
                                ('admin', 'Admin')],
                       default='user')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Form for user login.

    This form captures the necessary credentials for user login, specifically
    the username and password.

    Attributes:
        username (StringField): The username field, required for login.
        password (PasswordField): The password field, required for login.
        submit (SubmitField): The submission button.
    """
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Login')


class QuestionForm(FlaskForm):
    """Form for adding or editing a quiz question.

    This form captures the information required to create or update a quiz question,
    including the question text, four possible answers, and the correct answer.

    Attributes:
        question_text (TextAreaField): The field for the quiz question text.
        answer_a (StringField): The field for the first possible answer, labeled 'A'.
        answer_b (StringField): The field for the second possible answer, labeled 'B'.
        answer_c (StringField): The field for the third possible answer, labeled 'C'.
        answer_d (StringField): The field for the fourth possible answer, labeled 'D'.
        correct_answer (SelectField): The field for selecting the correct answer,
                                      with options A, B, C, or D.
        submit (SubmitField): The submission button.
    """
    question_text = TextAreaField('Question',
                                  validators=[DataRequired()])
    answer_a = StringField('Answer A',
                           validators=[DataRequired()])
    answer_b = StringField('Answer B',
                           validators=[DataRequired()])
    answer_c = StringField('Answer C',
                           validators=[DataRequired()])
    answer_d = StringField('Answer D',
                           validators=[DataRequired()])
    correct_answer = SelectField('Correct Answer',
                                 choices=[
                                     ('A', 'Answer A'),
                                     ('B', 'Answer B'),
                                     ('C', 'Answer C'),
                                     ('D', 'Answer D')
                                 ],
                                 validators=[DataRequired()])
    submit = SubmitField('Save Question')
