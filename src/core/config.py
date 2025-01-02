import os
from dotenv import load_dotenv

load_dotenv('.env') 

DATABASE_PATH = r"C:/Users/ckemplen/POLICY_DEVELOPMENT_APP/db.sqlite"
FILE_LIST = r"C:\Users\ckemplen\POLICY_DEVELOPMENT_APP\filelist.txt"

DB_URI = os.getenv('DB_URI')
DB_ECHO = os.getenv('DB_ECHO')
DOCANALYSIS_ENDPOINT = os.getenv('DOCANALYSIS_ENDPOINT')
