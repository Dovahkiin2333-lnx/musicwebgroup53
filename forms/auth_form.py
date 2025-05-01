from flask_wtf import FlaskForm
from models.models import EmailCaptchaModel, UserModel
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import Email, Length, EqualTo, InputRequired

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message="Email is required"),
        Email(message="Invalid email format")
    ])
    captcha = StringField('Verification Code', validators=[
        InputRequired(message="Verification code is required"),
        Length(min=4, max=4, message="Verification code must be 4 characters")
    ])
    username = StringField('Username', validators=[
        InputRequired(message="Username is required"),
        Length(min=3, max=20, message="Username must be 3-20 characters")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required"),
        Length(min=6, max=20, message="Password must be 6-20 characters")
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        InputRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise validators.ValidationError("This email is already registered")

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(
            email=email, 
            captcha=captcha
        ).first()
        if not captcha_model:
            raise validators.ValidationError("Invalid verification code")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message="Email is required"),
        Email(message="Invalid email format")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required"),
        Length(min=6, max=16, message="Password must be 6-16 characters")
    ])
    submit = SubmitField('Login')


class ChangePwForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        InputRequired(message="Current password is required"),
        Length(min=6, max=16, message="Password must be 6-16 characters")
    ])
    new_password = PasswordField('New Password', validators=[
        InputRequired(message="New password is required"),
        Length(min=6, max=16, message="Password must be 6-16 characters"),
        EqualTo('confirm_password', message="Passwords must match")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        InputRequired(message="Please confirm your new password")
    ])

class ChangeUsernameForm(FlaskForm):
    new_username = StringField('Username', validators=[
        InputRequired(message="Username is required"),
        Length(min=3, max=20, message="Username must be 3-20 characters")
    ])