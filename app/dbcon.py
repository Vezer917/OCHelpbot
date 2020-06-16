from dotenv import load_dotenv
import os

# Load dbfile env variable to pass to cogs
load_dotenv()
dbfile = os.getenv('DATABASE_FILE')