import sqlite3

from sqldb_scripts.config import  DB_PATH


def assign_employee_to_manager():

    manager_username = input("Manager username: ").strip()


    employee_id = input("Employee ID to assign: ").strip().upper()


    conn = sqlite3.connect( DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    try:

        manager = conn.execute(
            """
            SELECT
                user_id,
                role

            FROM users

            WHERE username = ?
            """,
            (
                manager_username,
            )
        ).fetchone()


        if manager is None:
            print("Manager user was not found.")
            return


        manager_user_id, role = manager


        if role != "manager":
            print("Selected user is not a manager.")
            return


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

            print("Employee was not found.")

            return


        conn.execute(
            """
            INSERT INTO manager_employee_access (
                manager_user_id,
                employee_id
            )

            VALUES (?, ?)

            ON CONFLICT (
                manager_user_id,
                employee_id
            )

            DO NOTHING
            """,
            (
                manager_user_id,
                employee_id
            )
        )


        conn.commit()


        print("Employee successfully assigned.")


    finally:

        conn.close()


if __name__ == "__main__":

    assign_employee_to_manager()