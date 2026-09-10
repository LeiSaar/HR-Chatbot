import csv
import sqlite3

from pathlib import Path

from sqldb_scripts.config import DB_PATH


PROJECT_ROOT = Path(__file__).resolve().parent.parent


CSV_PATH = PROJECT_ROOT/"data"/"employees.csv"



def import_employees():

    if not CSV_PATH.exists():

        raise FileNotFoundError( f"Employee CSV not found: {CSV_PATH}")

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    try:

        with open(CSV_PATH,"r", encoding="utf-8", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                conn.execute(
                    """
                    INSERT INTO employees (
                        employee_id,
                        name,
                        department,
                        position,
                        annual_leave,
                        used_leave,
                        remaining_leave,
                        performance
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(employee_id)
                    DO UPDATE SET

                        name = excluded.name,

                        department =
                            excluded.department,

                        position =
                            excluded.position,

                        annual_leave =
                            excluded.annual_leave,

                        used_leave =
                            excluded.used_leave,

                        remaining_leave =
                            excluded.remaining_leave,

                        performance =
                            excluded.performance
                    """,
                    (
                        row["employee_id"].strip(),

                        row["name"].strip(),

                        row["department"].strip(),

                        row["position"].strip(),

                        int(row["annual_leave"]),

                        int(row["used_leave"]),

                        int(row["remaining_leave"]),

                        row["performance"].strip()
                    )
                )

        conn.commit()

        print("Employees imported successfully.")

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


if __name__ == "__main__":

    import_employees()


# don't forget to import the employees csv file
# python -m sqldb_scripts.import_employees