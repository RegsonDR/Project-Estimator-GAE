from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, TelField, TimeField
from wtforms.fields import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


def validate_time(open_time, close_time):
    if open_time < close_time:
        raise ValidationError(open_time.data , " -: " , close_time.data)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    # Organization Details
    org_name = StringField('Organization Name', validators=[DataRequired()])
    org_phone = TelField('Organization Phone Number', validators=[DataRequired()])
    org_open = TimeField('Opening Time', validators=[DataRequired(), validate_time])
    org_close = TimeField('Closing Time', validators=[DataRequired()])
    # User Details
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    mobile_number = TelField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm_password', message="Passwords Must Match")])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')
