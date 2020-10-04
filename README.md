## OKANAGAN COLLEGE DISCORD BOT
============================

Written in Python3 with Flask framework

CURRENT FUNCTIONALITY:
======================
Flask:
- Register new users
- Add/Delete Custom Commands in Flask webportal
- Welcome message from bot upon joining Discord server
- User profiles

Discord Commands:
- !create-channel
- !profquote
- !addquote
- !links
- !help
- !quiz 
    - !makequiz
    - !quizlist
    - !addquestion 
- !roll_dice
- !courseinfo
- !register
- !whoami
- !whois
- Custom commands from Flask database

UPCOMING FUNCTIONALITY:
=======================
- add quizzes with flask forms
- add multiple return commands from flask

## Running

1. **Make sure to get Python 3.5 or higher**

This is required to actually run the bot.

2. **Set up venv**

Run in python: `python3.6 -m venv venv`

3. **Install dependencies**

This is `pip install -U -r requirements.txt` (full implementation not yet finished)

4. **Create the database in SQLite**

Will fill this out in greater detail in future 

5. **Setup configuration**

The next step is just to create a `config.py` file in the root directory where
the bot is with the following template:

```py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'insert-your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'name_of_your_database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
```

And a `.env` file in the root directory where the bot is with the
following template:

```
TOKEN=your_token_here
DATABASE_FILE = "your_db_here"
GUILDID=your_guild_ID_number_here
DEFINE_ID=the_dictionary_API_ID
DEFINE_KEY=the_dictionary_API_KEY
```

6. **Configuration of database**

To configure the SQLite database for use by the bot, go to the directory where your database file is located, and run:
 `python3.6 DiscordLaunch.py db init`
 `python3.6 app\routes.py db init`

## Requirements

- Python 3.6+
- v1.0.0 of discord.py
- Flask
- SQLite
