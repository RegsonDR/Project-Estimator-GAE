from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, TelField, TimeField
from wtforms.fields import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

#
# def validate_time(form,field):
#     if field.data > form.data['org_close']:
#         raise ValidationError("Opening time can not be higher than closing time!")


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    # Organization Details
    org_name = StringField('Organization Name', validators=[DataRequired()])
    org_phone = TelField('Organization Phone Number', validators=[DataRequired()])
    # User Details
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    mobile_number = TelField('Phone Number', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm_password', message="Passwords Must Match")])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')
