import os
import uuid
import re
import sqlite3
import json
import csv
import io
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_file
)

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

from werkzeug.security import (
    generate_password_hash
)

from werkzeug.utils import secure_filename

from dotenv import (
    load_dotenv
)


# =========================================================
# EXISTING PROJECT IMPORTS
# =========================================================

from src.auth import (
    authenticate_user,
    get_user_by_id
)

from src.conversation_manager import (
    create_conversation
)

from src.chat_orchestrator import (
    process_chat_message
)

from sqldb_scripts.config import (
    DB_PATH
)

load_dotenv()


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(
    __name__
)


app.secret_key = os.getenv(
    "FLASK_SECRET_KEY"
)


if not app.secret_key:

    raise RuntimeError(
        "FLASK_SECRET_KEY is not configured."
    )


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent


UPLOAD_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "uploads"
)


GENERATED_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "generated"
)


UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


GENERATED_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


app.config[
    "UPLOAD_FOLDER"
] = str(
    UPLOAD_FOLDER
)


app.config[
    "GENERATED_FOLDER"
] = str(
    GENERATED_FOLDER
)


# Maximum upload size:
# 20 MB

app.config[
    "MAX_CONTENT_LENGTH"
] = 20 * 1024 * 1024


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {

    "png",

    "jpg",

    "jpeg",

    "webp",

    "pdf",

    "csv",

    "txt",

    "docx"

}


def allowed_file(
    filename
):

    if not filename:

        return False


    if "." not in filename:

        return False


    extension = (
        filename
        .rsplit(
            ".",
            1
        )[1]
        .lower()
    )


    return (
        extension
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()


login_manager.init_app(
    app
)


login_manager.login_view = (
    "login"
)


@login_manager.user_loader
def load_user(
    user_id
):

    return get_user_by_id(
        user_id
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "index"
            )
        )


    if request.method == "GET":

        return render_template(
            "login.html"
        )


    username = request.form.get(
        "username",
        ""
    ).strip()


    password = request.form.get(
        "password",
        ""
    )


    user = authenticate_user(
        username,
        password
    )


    if user is None:

        return render_template(
            "login.html",

            error=(
                "Invalid username "
                "or password."
            )
        )


    login_user(
        user
    )


    return redirect(
        url_for(
            "index"
        )
    )


# =========================================================
# REGISTER
# =========================================================

EMPLOYEE_ID_PATTERN = re.compile(
    r"^EMP-\d{4}-\d{3}$"
)


@app.route(
    "/register",
    methods=[
        "GET",
        "POST"
    ]
)
def register():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "index"
            )
        )


    if request.method == "GET":

        return render_template(
            "register.html"
        )


    username = request.form.get(
        "username",
        ""
    ).strip()


    employee_id = request.form.get(
        "employee_id",
        ""
    ).strip().upper()


    password = request.form.get(
        "password",
        ""
    )


    password_confirmation = (
        request.form.get(
            "password_confirmation",
            ""
        )
    )


    if len(username) < 3:

        return render_template(
            "register.html",
            error=(
                "Username must contain "
                "at least 3 characters."
            )
        )


    if not EMPLOYEE_ID_PATTERN.fullmatch(
        employee_id
    ):

        return render_template(
            "register.html",
            error=(
                "Invalid employee ID format."
            )
        )


    if len(password) < 8:

        return render_template(
            "register.html",
            error=(
                "Password must contain "
                "at least 8 characters."
            )
        )


    if password != password_confirmation:

        return render_template(
            "register.html",
            error=(
                "Passwords do not match."
            )
        )


    conn = sqlite3.connect(
        DB_PATH
    )


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

            return render_template(
                "register.html",
                error=(
                    "Employee ID was not found."
                )
            )


        existing_employee = conn.execute(
            """
            SELECT user_id

            FROM users

            WHERE employee_id = ?
            """,
            (
                employee_id,
            )
        ).fetchone()


        if existing_employee:

            return render_template(
                "register.html",
                error=(
                    "This employee already "
                    "has an account."
                )
            )


        existing_username = conn.execute(
            """
            SELECT user_id

            FROM users

            WHERE username = ?
            """,
            (
                username,
            )
        ).fetchone()


        if existing_username:

            return render_template(
                "register.html",
                error=(
                    "Username is already in use."
                )
            )


        password_hash = (
            generate_password_hash(
                password
            )
        )


        conn.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                employee_id,
                role
            )

            VALUES (?, ?, ?, 'employee')
            """,
            (
                username,
                password_hash,
                employee_id
            )
        )


        conn.commit()


        return redirect(
            url_for(
                "login"
            )
        )


    except sqlite3.Error:

        conn.rollback()


        return render_template(
            "register.html",
            error=(
                "Could not create account."
            )
        )


    finally:

        conn.close()


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)
@login_required
def logout():

    logout_user()


    return redirect(
        url_for(
            "login"
        )
    )


# =========================================================
# CHAT PAGE
# =========================================================

@app.route(
    "/"
)
@login_required
def index():

    return render_template(
        "chat.html"
    )


# =========================================================
# CREATE CONVERSATION
# =========================================================

@app.route(
    "/conversations",
    methods=[
        "POST"
    ]
)
@login_required
def new_conversation():

    conversation_id = str(
        uuid.uuid4()
    )


    create_conversation(
        conversation_id=
            conversation_id,

        user_id=
            current_user.id,

        title=
            "New conversation"
    )


    return jsonify(
        {
            "conversation_id":
                conversation_id
        }
    )


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/chat",
    methods=[
        "POST"
    ]
)
@login_required
def chat():

    question = request.form.get(
        "msg",
        ""
    ).strip()


    conversation_id = (
        request.form.get(
            "conversation_id",
            ""
        ).strip()
    )


    uploaded_file = request.files.get(
        "file"
    )


    # -----------------------------------------------------
    # VALIDATE CONVERSATION
    # -----------------------------------------------------

    if not conversation_id:

        return jsonify(
            {
                "error":
                    "Missing conversation ID."
            }
        ), 400


    # -----------------------------------------------------
    # VALIDATE MESSAGE / FILE
    # -----------------------------------------------------

    if not question and (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):

        return jsonify(
            {
                "error":
                    "Please enter a question "
                    "or upload a file."
            }
        ), 400


       # -----------------------------------------------------
    # HANDLE FILE UPLOAD
    # -----------------------------------------------------

    uploaded_file_info = None


    if uploaded_file is not None:

        if (
            uploaded_file.filename
            and not allowed_file(
                uploaded_file.filename
            )
        ):

            return jsonify(
                {
                    "error":
                        "Unsupported file type."
                }
            ), 400


        if uploaded_file.filename:

            original_filename = (
                secure_filename(
                    uploaded_file.filename
                )
            )


            unique_filename = (
                str(uuid.uuid4())
                + "_"
                + original_filename
            )


            saved_path = (
                UPLOAD_FOLDER
                / unique_filename
            )


            uploaded_file.save(
                saved_path
            )


            uploaded_file_info = {
                "path": str(saved_path),
                "extension": saved_path.suffix.lower()
            }

    # -----------------------------------------------------
    # NORMAL CHAT
    # -----------------------------------------------------

    try:

        result = (
            process_chat_message(
                user=current_user,
                conversation_id=conversation_id,
                question=question,
                uploaded_file=uploaded_file_info
                )
        )


        if not result[
            "success"
        ]:

            return jsonify(
                {
                    "error":
                        result[
                            "answer"
                        ]
                }
            ), result[
                "status_code"
            ]


        return jsonify(
            {
                "answer": result["answer"],

                "question": result["question"],

                "route": result["route"],

                "generated_files": result.get("generated_files", [])
            }
        )


    except Exception as error:

        app.logger.exception(
            "Chat processing error"
        )


        return jsonify(
            {
                "error":
                    (
                        "An unexpected error "
                        "occurred while processing "
                        "your request."
                    )
            }
        ), 500


# =========================================================
# DOWNLOAD GENERATED FILE
# =========================================================

@app.route(
    "/generated/<filename>"
)
@login_required
def download_generated_file(
    filename
):

    safe_filename = (
        secure_filename(
            filename
        )
    )


    file_path = (
        GENERATED_FOLDER
        / safe_filename
    )


    if not file_path.exists():

        return jsonify(
            {
                "error":
                    "File not found."
            }
        ), 404


    return send_file(
        file_path,
        as_attachment=True
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",

        port=5000,

        debug=True
    )