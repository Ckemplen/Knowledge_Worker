import os
from dotenv import load_dotenv

load_dotenv(".env")

DATABASE_PATH = os.getenv("DB_URI")
FILE_LIST = os.getenv("FILE_LIST")

DB_URI = os.getenv("DB_URI")
DB_ECHO = os.getenv("DB_ECHO")
DOCANALYSIS_ENDPOINT = os.getenv("DOCANALYSIS_ENDPOINT")
CANONICAL_ENTITIES_CONSOLIDATION_ENDPOINT = os.getenv(
    "CANONICAL_ENTITIES_CONSOLIDATION_ENDPOINT"
)
