from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, DateField, TextAreaField
from wtforms.validators import DataRequired


class NewWorkspace(FlaskForm):
    workspace_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = TextAreaField('Project Description', validators=[DataRequired()])
    project_deadline = DateField('Project Deadline', validators=[DataRequired()])
    submit = SubmitField('Create')
