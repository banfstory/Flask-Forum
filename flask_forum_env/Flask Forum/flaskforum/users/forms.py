from flaskforum.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from flaskforum import bcrypt

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30, message="*Username must be between 4 and 25 characters.")])
    email = StringField('Email', validators=[InputRequired(),Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('*This username is unavailable.')
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('*This email is unavailable.')

class AccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30, message="*Username must be between 4 and 25 characters.")])
    email = StringField('Email', validators=[InputRequired(),Email()])
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg','png','bmp'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data!=current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('*This username is unavailable.')
    
    def validate_email(self, email):
        if email.data!=current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('*This email is unavailable.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError('*The old password you entered was incorrect. Please try again.')