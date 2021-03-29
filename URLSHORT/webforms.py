from flask_wtf import FlaskForm as Form, RecaptchaField
from wtforms import StringField, SelectField, PasswordField, validators

#Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1,max=45)])
    username = StringField('Username', [validators.Length(min=1,max=20)])
    email = StringField('Email', [validators.Length(min=1,max=100)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class CreateUrlForm(Form):
    url_main = StringField('Name', [validators.Length(min=5,max=500)])

class ChangePassword(Form):
    old_password = PasswordField('Old Password', [validators.DataRequired()])

    new_password = PasswordField('New Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='New passwords do not match')
    ])
    confirm = PasswordField('Confirm New Password')