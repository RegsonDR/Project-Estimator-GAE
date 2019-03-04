from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from wtforms.validators import DataRequired


class NewOrganisation(FlaskForm):
    org_name = StringField('Organization Name', validators=[DataRequired()])
    org_phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewProject(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = StringField('Project Description', validators=[DataRequired()])
    # project_status = StringField('Project Status', validators=[DataRequired()])
    # project_stage = StringField('Project Stage', validators=[DataRequired()])
    submit = SubmitField('Create')
