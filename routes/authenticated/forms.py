from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from wtforms.validators import DataRequired


class NewOrganisation(FlaskForm):
    org_name = StringField('Organization Name', validators=[DataRequired()])
    org_phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Create')

