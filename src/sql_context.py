import sqlite3
import json
from sqldb_scripts.config import DB_PATH
from src.access_control import check_employee_access

def get_employee(employee_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """SELECT employee_id, name, department, position, annual_leave, 
                      used_leave, remaining_leave, performance 
               FROM employees WHERE employee_id = ?""",
            (employee_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_sql_context(question, user):
    access_result = check_employee_access(user, question)

    if not access_result["allowed"]:
        return {"allowed": False, "context": "ACCESS_DENIED", "employee_id": access_result["requested_employee_id"]}

    employee_id = access_result["requested_employee_id"]
    employee = get_employee(employee_id)

    if employee is None:
        return {"allowed": True, "context": f"No employee with ID {employee_id} was found.", "employee_id": employee_id}

    context = json.dumps(employee, indent=2)
    return {
        "allowed": True,
        "context": f"EMPLOYEE DATABASE (Authoritative Data for {employee_id}):\n{context}",
        "employee_id": employee_id
    }