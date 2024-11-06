from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    """Form for user registration.

    This form captures the necessary information for user registration,
    including username and password fields with validation.

    Attributes:
        username (StringField): The username field.
        password (PasswordField): The password field.
        password2 (PasswordField): The field for confirming the password.
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
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Form for user login.

    This form captures the necessary credentials for user login.

    Attributes:
        username (StringField): The username field.
        password (PasswordField): The password field.
        submit (SubmitField): The submission button.
    """
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Login')


class QuestionForm(FlaskForm):
    """Form for adding a quiz question.

    This form captures the information required to create a quiz question,
    including the question text and possible answers.

    Attributes:
        question_text (TextAreaField): The field for the quiz question text.
        answer_a (StringField): The field for the first possible answer.
        answer_b (StringField): The field for the second possible answer.
        answer_c (StringField): The field for the third possible answer.
        answer_d (StringField): The field for the fourth possible answer.
        correct_answer (SelectField): The field for selecting the correct
            answer.
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
