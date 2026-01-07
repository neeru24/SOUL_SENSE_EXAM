import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "soulsense_db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
