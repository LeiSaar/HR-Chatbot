from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_DIR = PROJECT_ROOT/"database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR/"hr_chatbot.db"

SCHEMA_PATH = PROJECT_ROOT/"sqldb_scripts"/"schema.sql"