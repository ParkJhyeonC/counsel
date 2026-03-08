from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "data" / "counsel.db"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "hwp", "txt"}


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @app.before_request
    def before_request() -> None:
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception: Exception | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.route("/")
    def index() -> str:
        students = query_db(
            "SELECT id, student_no, name, class_name FROM students ORDER BY class_name, name"
        )
        latest_logs = query_db(
            """
            SELECT l.id, l.date, l.type, s.name AS student_name, l.summary
            FROM counsel_logs l
            JOIN students s ON s.id = l.student_id
            ORDER BY l.date DESC, l.created_at DESC
            LIMIT 10
            """
        )
        return render_template("index.html", students=students, latest_logs=latest_logs)

    @app.route("/students", methods=["GET", "POST"])
    def students() -> str:
        if request.method == "POST":
            student_no = request.form.get("student_no", "").strip()
            name = request.form.get("name", "").strip()
            class_name = request.form.get("class_name", "").strip()
            phone = request.form.get("phone", "").strip()
            guardian_phone = request.form.get("guardian_phone", "").strip()
            note = request.form.get("note", "").strip()

            if not student_no or not name:
                flash("학번과 이름은 필수입니다.")
            else:
                try:
                    execute_db(
                        """
                        INSERT INTO students(student_no, name, class_name, phone, guardian_phone, note)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (student_no, name, class_name, phone, guardian_phone, note),
                    )
                    flash("학생 정보가 저장되었습니다.")
                    return redirect(url_for("students"))
                except sqlite3.IntegrityError:
                    flash("이미 등록된 학번입니다.")

        q = request.args.get("q", "").strip()
        if q:
            student_rows = query_db(
                """
                SELECT id, student_no, name, class_name, phone, guardian_phone, note
                FROM students
                WHERE student_no LIKE ? OR name LIKE ? OR class_name LIKE ?
                ORDER BY class_name, name
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%"),
            )
        else:
            student_rows = query_db(
                """
                SELECT id, student_no, name, class_name, phone, guardian_phone, note
                FROM students
                ORDER BY class_name, name
                """
            )
        return render_template("students.html", students=student_rows, q=q)

    @app.route("/logs/new", methods=["GET", "POST"])
    def new_log() -> str:
        student_rows = query_db("SELECT id, student_no, name, class_name FROM students ORDER BY class_name, name")
        if request.method == "POST":
            student_id = request.form.get("student_id", "").strip()
            date = request.form.get("date", "").strip()
            log_type = request.form.get("type", "").strip()
            summary = request.form.get("summary", "").strip()
            detail = request.form.get("detail", "").strip()
            action_plan = request.form.get("action_plan", "").strip()
            next_date = request.form.get("next_date", "").strip()

            if not student_id or not date or not log_type or not summary:
                flash("학생, 상담일, 상담유형, 상담요약은 필수입니다.")
            else:
                log_id = execute_db(
                    """
                    INSERT INTO counsel_logs(student_id, date, type, summary, detail, action_plan, next_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        date,
                        log_type,
                        summary,
                        detail,
                        action_plan,
                        next_date or None,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )

                files = request.files.getlist("attachments")
                for file in files:
                    if not file or file.filename == "":
                        continue
                    if allowed_file(file.filename):
                        original_name = file.filename
                        ext = original_name.rsplit(".", 1)[1].lower()
                        new_name = f"{uuid.uuid4().hex}.{ext}"
                        save_path = UPLOAD_DIR / secure_filename(new_name)
                        file.save(save_path)
                        execute_db(
                            """
                            INSERT INTO attachments(log_id, file_path, original_name, created_at)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                log_id,
                                save_path.name,
                                secure_filename(original_name),
                                datetime.now().isoformat(timespec="seconds"),
                            ),
                        )

                flash("상담일지가 저장되었습니다.")
                return redirect(url_for("student_detail", student_id=student_id))

        return render_template("new_log.html", students=student_rows)

    @app.route("/students/<int:student_id>")
    def student_detail(student_id: int) -> str:
        student = query_db(
            "SELECT id, student_no, name, class_name, phone, guardian_phone, note FROM students WHERE id = ?",
            (student_id,),
            one=True,
        )
        if student is None:
            flash("학생을 찾을 수 없습니다.")
            return redirect(url_for("students"))

        log_rows = query_db(
            """
            SELECT id, date, type, summary, detail, action_plan, next_date, created_at
            FROM counsel_logs
            WHERE student_id = ?
            ORDER BY date DESC, created_at DESC
            """,
            (student_id,),
        )
        logs_with_files: list[dict[str, Any]] = []
        for row in log_rows:
            files = query_db(
                "SELECT id, file_path, original_name FROM attachments WHERE log_id = ? ORDER BY id",
                (row["id"],),
            )
            logs_with_files.append({"log": row, "files": files})

        return render_template("student_detail.html", student=student, logs=logs_with_files)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

    @app.route("/init-db")
    def init_db_route() -> str:
        init_db()
        flash("데이터베이스를 초기화했습니다.")
        return redirect(url_for("index"))

    return app


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class_name TEXT,
                phone TEXT,
                guardian_phone TEXT,
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS counsel_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                summary TEXT NOT NULL,
                detail TEXT,
                action_plan TEXT,
                next_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                original_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(log_id) REFERENCES counsel_logs(id)
            );
            """
        )
    conn.close()


def query_db(query: str, params: tuple[Any, ...] = (), one: bool = False):
    cur = g.db.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query: str, params: tuple[Any, ...] = ()) -> int:
    cur = g.db.execute(query, params)
    g.db.commit()
    row_id = cur.lastrowid
    cur.close()
    return row_id


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
