from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User, Command


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

# This is the Custom Command Form that appears on the main page:


class CmdForm(FlaskForm):
    cmdname = StringField('Command Name', validators=[DataRequired()])
    context = SelectField(u'Context', choices=[('onMessage', 'onMessage'), ('onJoin', 'onJoin'), ('onReact', 'onReact')])
    cmdvalue = TextAreaField('Command Return', validators=[DataRequired()])
    help = TextAreaField('Help Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_cmdname(self, cmdname):
            cmd = Command.query.filter_by(name=cmdname.data).first()
            if cmd is not None:
                raise ValidationError('Please use a different command name.')


class DelCmdForm(FlaskForm):
    name = StringField('Command Name', validators=[DataRequired()])
    submit = SubmitField('Delete')

    def validate_delcmdname(self, name):
        name = Command.query.filter_by(name=name.data).first()
        if name is None:
            raise ValidationError('No command by that name exists.')