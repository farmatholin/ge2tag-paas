from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(Form):
    """Login form to access writing and settings pages"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class SignUpForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class CreateContainer(Form):
    name = StringField('Name', validators=[DataRequired()])
    cpu = IntegerField("cpu", validators=[DataRequired()])
    ram = IntegerField("ram", validators=[DataRequired()])
