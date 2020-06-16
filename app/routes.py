from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, Blueprint, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm, CmdForm, DelCmdForm
from app.models import User, Command, Quiz
from app.email import send_password_reset_email

commands_blueprint = Blueprint('commands', __name__, template_folder='templates')
users_blueprint = Blueprint('userlist', __name__, template_folder='templates')
quiz_blueprint = Blueprint('quizlist', __name__, template_folder='templates')


@commands_blueprint.route('/')
def index():
    all_commands = Command.query.all()
    return render_template('commands.html', commands=all_commands)


@users_blueprint.route('/')
def index():
    all_users = User.query.all()
    return render_template('userlist.html', users=all_users)


@quiz_blueprint.route('/')
def index():
    all_quiz = Quiz.query.all()
    return render_template('quiz.html', quiz=all_quiz)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CmdForm()

    if form.validate_on_submit():
        if current_user.admin == 0:
            flash('You are not an admin. Please request to be an admin.')
        if current_user.admin == 1:
            cmdnew = Command(name=form.cmdname.data, context=form.context.data, value=form.cmdvalue.data,
                         author=current_user.username, help=form.help.data)
            db.create_all()
            db.session.add(cmdnew)
            db.session.commit()
            flash('Command successfully added')
            redirect(url_for('command_list'))
    return render_template('index.html', title='Home', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db.create_all()
        # temporarily turned off admin=0 for testing purposes
        # user = User(username=form.username.data, email=form.email.data, admin=0)
        user = User(username=form.username.data, email=form.email.data, admin=1)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/commands', methods=['GET', 'POST'])
@login_required
def command_list():
    form = DelCmdForm()
    if form.validate_on_submit():
        delcmd = Command.query.filter_by(name=form.name.data).first()
        db.session.delete(delcmd)
        db.session.commit()
        return redirect(url_for('command_list'))
    commands = Command.query.all()
    return render_template('commands.html', commands=commands, title='Command List', form=form)


@app.route('/userlist')
@login_required
def userlist():
    if current_user.admin == 0:
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('userlist.html', users=users, title='User List')


@app.route('/usermanual')
def usermanual():
    return render_template('usermanual.html', title='User Manual')


@app.route('/quiz')
def quizpage():
    return render_template('quiz.html', title='Quiz')
