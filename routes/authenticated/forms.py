from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, DateField, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class NewWorkspace(FlaskForm):
    workspace_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', widget=TextArea(), validators=[DataRequired()])
    project_deadline = StringField('Project Deadline', validators=[DataRequired()])
    submit = SubmitField('Create')
