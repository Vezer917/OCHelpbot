from dotenv import load_dotenv
import os
import sqlite3

# Load dbfile env variable to pass to cogs
load_dotenv()
dbfile = os.getenv('DATABASE_FILE')

conn = sqlite3.connect(dbfile)
c = conn.cursor()
