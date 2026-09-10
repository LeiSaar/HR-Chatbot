import getpass
import re
import sqlite3

from werkzeug.security import generate_password_hash

from sqldb_scripts.config import DB_PATH

VALID_ROLES = {"employee","manager","hr_admin"}

EMPLOYEE_ID_PATTERN = re.compile( r"^EMP-\d{4}-\d{3}$")

def create_user():

    username = input( "Username: ").strip()


    employee_id = input("Employee ID: ").strip().upper()


    role = input("Role [employee/manager/hr_admin]: ").strip().lower()


    password = getpass.getpass( "Password: ")


    confirmation = getpass.getpass( "Confirm password: ")


    if len(username) < 3:

        print("Username must contain at least 3 characters.")
        return


    if not EMPLOYEE_ID_PATTERN.fullmatch(employee_id):

        print( "Invalid employee ID.")
        return


    if role not in VALID_ROLES:

        print( "Invalid role." )
        return


    if len(password) < 8:

        print( "Password must contain at least 8 characters." )
        return


    if password != confirmation:

        print("Passwords do not match.")
        return


    conn = sqlite3.connect(DB_PATH)

    conn.execute( "PRAGMA foreign_keys = ON")

    try:

        employee = conn.execute(
            """
            SELECT employee_id

            FROM employees

            WHERE employee_id = ?
            """,
            (
                employee_id,
            )
        ).fetchone()


        if employee is None:

            print(
                "Employee does not exist."
            )

            return


        existing = conn.execute(
            """
            SELECT user_id

            FROM users

            WHERE employee_id = ?

            OR username = ?
            """,
            (
                employee_id,
                username
            )
        ).fetchone()


        if existing:

            print("Username or employee already has an account.")
            return


        password_hash = (
            generate_password_hash(password)
        )


        conn.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                employee_id,
                role
            )

            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                employee_id,
                role
            )
        )


        conn.commit()


        print("User created successfully.")


    except sqlite3.Error as error:

        conn.rollback()

        print(f"Database error: {error}")


    finally:

        conn.close()


if __name__ == "__main__":

    create_user()