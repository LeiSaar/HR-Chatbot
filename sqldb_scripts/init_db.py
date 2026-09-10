import sqlite3

from sqldb_scripts.config import  DB_PATH, SCHEMA_PATH

def init_database():

    print(
        f"Initializing database: {DB_PATH}"
    )

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        with open( SCHEMA_PATH, "r", encoding="utf-8") as schema_file:

            schema = schema_file.read()

        conn.executescript(schema)

        conn.commit()

    print( "Database initialized successfully.")


if __name__ == "__main__":

    init_database()


# don't forget to initialise the database
# python -m sqldb_scripts.init_db