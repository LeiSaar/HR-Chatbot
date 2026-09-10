import sqlite3

from sqldb_scripts.config import DB_PATH


def create_conversation(conversation_id, user_id, title="New conversation"):

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    try:
        conn.execute(
            """
            INSERT INTO conversations (
                conversation_id,
                user_id,
                title
            )

            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                user_id,
                title
            )
        )

        conn.commit()

    finally:

        conn.close()


def user_owns_conversation(conversation_id, user_id):

    conn = sqlite3.connect(DB_PATH)

    try:

        result = conn.execute(
            """
            SELECT 1

            FROM conversations

            WHERE conversation_id = ?

            AND user_id = ?

            LIMIT 1
            """,
            (
                conversation_id,
                user_id
            )
        ).fetchone()


        return result is not None


    finally:

        conn.close()


def update_conversation_timestamp(conversation_id):

    conn = sqlite3.connect(DB_PATH)

    try:

        conn.execute(
            """
            UPDATE conversations

            SET updated_at =
                CURRENT_TIMESTAMP

            WHERE conversation_id = ?
            """,
            (
                conversation_id,
            )
        )


        conn.commit()


    finally:

        conn.close()


def save_database_message(conversation_id, role, content):

    conn = sqlite3.connect(DB_PATH)

    try:

        conn.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )

            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content
            )
        )


        conn.commit()


    finally:

        conn.close()