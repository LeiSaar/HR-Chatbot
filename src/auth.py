import sqlite3

from flask_login import UserMixin

from werkzeug.security import check_password_hash


from sqldb_scripts.config import DB_PATH


class User(UserMixin):

    def __init__(self, user_id, username, employee_id, role, is_active=True):

        self.id = user_id

        self.username = username

        self.employee_id = employee_id

        self.role = role

        self.is_active_user = bool(is_active)


    @property
    def is_active(self):

        return self.is_active_user


    @property
    def is_employee(self):

        return self.role == "employee"
        


    @property
    def is_manager(self):

        return self.role == "manager"


    @property
    def is_hr_admin(self):

        return self.role == "hr_admin"


def get_user_by_id(user_id):

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    try:

        row = conn.execute(
            """
            SELECT
                user_id,
                username,
                employee_id,
                role,
                is_active

            FROM users

            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()


        if row is None:

            return None


        return User(

            user_id=row["user_id"],

            username=row["username"],

            employee_id=row["employee_id"],

            role=row["role"],

            is_active=bool(
                row["is_active"]
            )
        )

    finally:

        conn.close()


def authenticate_user(username, password):

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    try:

        row = conn.execute(
            """
            SELECT
                user_id,
                username,
                password_hash,
                employee_id,
                role,
                is_active

            FROM users

            WHERE username = ?
            """,
            (
                username,
            )
        ).fetchone()


        if row is None:

            return None


        if not row["is_active"]:

            return None


        if not check_password_hash(row["password_hash"], password):

            return None


        return User(

            user_id=row["user_id"],

            username=row["username"],

            employee_id=row["employee_id"],

            role=row["role"],

            is_active=bool(
                row["is_active"]
            )
        )

    finally:

        conn.close()