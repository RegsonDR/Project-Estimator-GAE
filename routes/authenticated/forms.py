from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.fields import SubmitField, StringField, SelectField, PasswordField, SelectMultipleField
from wtforms.fields.html5 import EmailField, TelField, IntegerField, URLField
from wtforms.widgets import TextArea, html_params, HTMLString
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, regexp
from cgi import escape
from datetime import datetime

def validate_dates(form,field):
    start = datetime.strptime(field.data, '%d/%m/%Y').date()
    end = datetime.strptime(form.data['project_deadline'], '%d/%m/%Y').date()
    if start > end:
        raise ValidationError("Start date can not be higher than deadline date!")

def validate_task_dates(form,field):
    start = datetime.strptime(field.data, '%d/%m/%Y').date()
    end = datetime.strptime(form.data['task_finishbydate'], '%d/%m/%Y').date()
    if start > end:
        raise ValidationError("Task start date can not be higher than deadline date!")

class NewWorkspace(FlaskForm):
    workspace_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', widget=TextArea(), validators=[DataRequired()])
    project_start = StringField('Project Start', validators=[DataRequired(), validate_dates])
    project_deadline = StringField('Project Deadline', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewUser(FlaskForm):
    user_email = EmailField("User's Email", validators=[DataRequired()])
    role = SelectField("Role", choices=[("developer", "Developer"), ("manager", "Manager"), ("admin","Admin")], validators=[DataRequired()])
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
    project_start = StringField('Project Start', validators=[DataRequired(), validate_dates])
    project_deadline = StringField('Project Deadline', validators=[DataRequired()])
    project_status = SelectField('Project Status',
                                 choices=[("Running", "Running"), ("Closed", "Closed"), ("On Hold", "On Hold")],
                                 validators=[DataRequired()])
    project_manager = SelectField('Project Manager', validators=[DataRequired()])
    project_stage = StringField('Project Stage', validators=[DataRequired()])
    project_function_points = IntegerField('Functional Points')
    submit = SubmitField('Save')

class Task(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    task_description = StringField('Task Description', widget=TextArea(), validators=[DataRequired()])
    task_aminutes = IntegerField('Allocated Minutes', validators=[DataRequired()])
    task_skills = SelectMultipleField('Skills Required', choices=[("2", "Python"), ("1", "Java")], validators=[DataRequired()])
    task_startdate =StringField('Task Start', validators=[DataRequired(), validate_task_dates])
    task_finishbydate = StringField('Task Finish', validators=[DataRequired()])
    task_developers = SelectMultipleField('Allocated Developers', validators=[DataRequired()])
    parent_task = SelectField('Parent Task')
    task_status = SelectField('Task Status', choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])
    submit = SubmitField('Save')

class LogTask(FlaskForm):
    log_minutes = IntegerField('Time Spent (Minutes)', validators=[DataRequired()])
    log_comments = StringField('Comments', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Save')

class AddSkill(FlaskForm):
    skill_name = SelectField('Skill Name', validators=[DataRequired()])
    submit = SubmitField('Add')

class WKSettings(FlaskForm):
    workspace_name = StringField('Workspace Name', validators=[DataRequired()])
    allow_dev_skills = SelectField('Allow Developers to set their skills', choices=[("False", "No"), ("True", "Yes")], validators=[DataRequired()])
    api_key = StringField('API Key', validators=[DataRequired()], render_kw ={'readonly': True})
    enable_api = SelectField('Enable API Access?', choices=[("False", "No"), ("True", "Yes")], validators=[DataRequired()])
    webhook_url = URLField('Webhook URL', validators=[])
    enable_webhook = SelectField('Enable Webhook?', choices=[("False", "No"), ("True", "Yes")], validators=[DataRequired()])
    submit = SubmitField('Save')

class UploadHistorical(FlaskForm):
    file = FileField("Historical Data",validators=[FileRequired()])
    save = SubmitField('Upload')
