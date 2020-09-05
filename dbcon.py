from dotenv import load_dotenv
import os
import sqlite3

# Load dbfile env variable to pass to cogs
load_dotenv()
dbfile = os.getenv('DATABASE_FILE')


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


conn = sqlite3.connect(dbfile)
c = conn.cursor()
