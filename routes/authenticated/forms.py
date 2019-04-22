from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectField, PasswordField, SelectMultipleField
from wtforms.fields.html5 import EmailField, TelField, IntegerField
from wtforms.widgets import TextArea, html_params, HTMLString
from wtforms.validators import DataRequired, Email, EqualTo
from cgi import escape

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
    role = SelectField("Role", choices=[("developer", "Developer"), ("manager", "Manager")], validators=[DataRequired()])
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
    project_status = SelectField('Project Status',
                                 choices=[("Running", "Running"), ("Closed", "Closed"), ("On Hold", "On Hold")],
                                 validators=[DataRequired()])
    project_manager = SelectField('Project Manager', validators=[DataRequired()])
    project_stage = StringField('Project Stage', validators=[DataRequired()])
    submit = SubmitField('Save')

class Task(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    task_description = StringField('Task Description', widget=TextArea(), validators=[DataRequired()])
    task_aminutes = IntegerField('Allocated Minutes', validators=[DataRequired()])
    task_skills = SelectMultipleField('Skills Required', choices=[("2", "Python"), ("1", "Java")], validators=[DataRequired()])
    task_developers = SelectMultipleField('Allocated Developers', validators=[DataRequired()])
    task_status = SelectField('Task Status', choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])
    submit = SubmitField('Save')

class LogTask(FlaskForm):
    log_minutes = IntegerField('Time Spent (Minutes)', validators=[DataRequired()])
    log_comments = StringField('Comments', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Save')
