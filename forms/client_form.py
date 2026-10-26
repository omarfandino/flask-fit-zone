from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ClientForm(FlaskForm):
    id = HiddenField(validators=[Optional()])
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(max=50)],
    )
    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(max=50)],
    )
    membership = IntegerField(
        "Membership",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    submit = SubmitField("Save")
