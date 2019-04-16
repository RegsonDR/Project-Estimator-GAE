from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, DateField
from wtforms.validators import DataRequired


class NewWorkspace(FlaskForm):
    workspace_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', validators=[DataRequired()])
    project_deadline = DateField('Project Deadline', validators=[DataRequired()])

    # project_status = StringField('Project Status', validators=[DataRequired()])
    # project_stage = StringField('Project Stage', validators=[DataRequired()])
    submit = SubmitField('Create')
