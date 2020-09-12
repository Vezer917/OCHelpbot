from dotenv import load_dotenv
import os
import sqlite3
from sqlalchemy import create_engine

# The function of this file is to create a centralized point for database connections

load_dotenv()
dbfile = os.getenv('DATABASE_FILE')

# create an engine for SQLAlchemy to use
# if you set echo=True then you will get a printout of each query to the DB, pretty useful
engine = create_engine('sqlite:///'+dbfile, echo=False)

conn = sqlite3.connect(dbfile)
c = conn.cursor()


# this method just cleans strings to protect against injection
def sanitize(self):
    """
    :type self: String
    """
    specials = ["!", "'", "$", ";", "-"]
    clean_string = ""
    for char in self:
        if char not in specials:
            clean_string += char
    return clean_string
