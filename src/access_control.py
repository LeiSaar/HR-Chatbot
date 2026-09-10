import re
import sqlite3

from sqldb_scripts.config import DB_PATH


EMPLOYEE_ID_PATTERN = re.compile(r"EMP-\d{4}-\d{3}", re.IGNORECASE)

def extract_employee_id(text):

    match = EMPLOYEE_ID_PATTERN.search(text)

    if match is None:

        return None

    return match.group(0).upper()


def can_access_employee(user, target_employee_id):

    target_employee_id = target_employee_id.upper()

    # Employees can only access
    # their own employee record.

    if user.role == "employee":

        return target_employee_id == user.employee_id.upper()

    # Managers can access:
    # 1. themselves
    # 2. explicitly assigned employees

    if user.role == "manager":

        if (target_employee_id == user.employee_id.upper()):
            return True


        conn = sqlite3.connect(DB_PATH)

        try:

            result = conn.execute(
                """
                SELECT 1

                FROM manager_employee_access

                WHERE manager_user_id = ?

                AND employee_id = ?

                LIMIT 1
                """,
                (
                    user.id,
                    target_employee_id
                )
            ).fetchone()


            return result is not None


        finally:

            conn.close()


    # HR admins can access all
    # employee information.

    if user.role == "hr_admin":
        return True

    return False


def check_employee_access(user, question):

    requested_employee_id = extract_employee_id(question)

    # If the user didn't specify
    # an employee ID, interpret the
    # question as referring to themselves.

    if requested_employee_id is None:

        target_employee_id = user.employee_id

    else:

        target_employee_id = requested_employee_id


    allowed = can_access_employee(user, target_employee_id)

    if not allowed:

        return {
            "allowed": False,

            "requested_employee_id": target_employee_id,

            "reason": "user_not_authorised"
        }


    return {
        "allowed": True,

        "requested_employee_id": target_employee_id,

        "reason": "authorised"
    }