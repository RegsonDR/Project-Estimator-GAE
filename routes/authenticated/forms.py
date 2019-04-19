from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, EqualTo



class NewWorkspace(FlaskForm):
    workspace_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', widget=TextArea(), validators=[DataRequired()])
    project_deadline = StringField('Project Deadline', validators=[DataRequired()])
    submit = SubmitField('Create')

class NewUser(FlaskForm):
    user_email = EmailField("User's Email", validators=[DataRequired()])
    role = SelectField("Role",choices=[("dev","Developer"),("super-dev","Super Developer"),("manager","Manager")], validators=[DataRequired()])
    submit = SubmitField('Add')

class ProfileUser(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    mobile_number = TelField('Phone Number', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[EqualTo('confirm_password', message="Passwords Must Match")])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Save')

class Project(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', widget=TextArea(), validators=[DataRequired()])
    project_deadline = StringField('Project Deadline', validators=[DataRequired()])
    project_status = SelectField('Project Status',choices=[("Running","Running"),("Closed","Closed"),("On Hold","On Hold")], validators=[DataRequired()])
    project_manager = SelectField('Project Manager',choices=[("Running","Running"),("Closed","Closed"),("On Hold","On Hold")], validators=[DataRequired()])
    project_stage = StringField('Project Stage', validators=[DataRequired()])
    submit = SubmitField('Create')

