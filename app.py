from __future__ import annotations

import os
import sqlite3
import uuid
import zipfile
from calendar import Calendar, monthrange
from datetime import date, datetime
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

BASE_DIR = Path(__file__).resolve().parent
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "hwp", "txt"}

PROJECT_ROOT = BASE_DIR
TEMPLATE_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
DB_PATH = PROJECT_ROOT / "data" / "counsel.db"
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
BACKUP_DIR = PROJECT_ROOT / "data" / "backups"
MAX_BACKUP_FILES = 20


def validate_project_layout() -> None:
    required_files = [
        PROJECT_ROOT / "app.py",
        TEMPLATE_DIR / "index.html",
        TEMPLATE_DIR / "base.html",
        STATIC_DIR / "style.css",
    ]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "프로젝트 폴더 구조를 찾을 수 없습니다. app.py와 templates/static 파일이 같은 프로젝트 루트에 있어야 합니다. "
            f"누락 파일: {missing}"
        )


def create_app() -> Flask:
    validate_project_layout()

    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
    )
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

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
        upcoming_schedules = query_db(
            """
            SELECT c.id, c.schedule_date, c.schedule_time, c.title, c.status, s.name AS student_name
            FROM counsel_schedules c
            LEFT JOIN students s ON s.id = c.student_id
            WHERE c.status = 'planned' AND c.schedule_date >= ?
            ORDER BY c.schedule_date ASC, c.schedule_time ASC, c.id ASC
            LIMIT 7
            """,
            (datetime.now().date().isoformat(),),
        )
        backup_files = list_backup_files()
        return render_template(
            "index.html",
            students=students,
            latest_logs=latest_logs,
            upcoming_schedules=upcoming_schedules,
            backup_files=backup_files,
        )

    @app.route("/backup/create", methods=["POST"])
    def create_backup() -> str:
        backup_name = create_backup_archive(trigger="manual")
        flash(f"백업 파일을 생성했습니다: {backup_name}")
        return redirect(url_for("index"))

    @app.route("/backup/download/<path:filename>")
    def download_backup(filename: str):
        return send_from_directory(BACKUP_DIR, filename, as_attachment=True)

    @app.route("/schedule", methods=["GET", "POST"])
    def schedule() -> str:
        requested_date = request.args.get("date", "").strip()
        try:
            selected_date_obj = date.fromisoformat(requested_date) if requested_date else datetime.now().date()
        except ValueError:
            selected_date_obj = datetime.now().date()
        selected_date = selected_date_obj.isoformat()

        month_param = request.args.get("month", "").strip()
        try:
            if month_param:
                year, month = month_param.split("-")
                calendar_year = int(year)
                calendar_month = int(month)
            else:
                calendar_year = selected_date_obj.year
                calendar_month = selected_date_obj.month
        except ValueError:
            calendar_year = selected_date_obj.year
            calendar_month = selected_date_obj.month

        first_day_of_month = date(calendar_year, calendar_month, 1)
        last_day_of_month = date(calendar_year, calendar_month, monthrange(calendar_year, calendar_month)[1])
        prev_month = date(calendar_year - 1, 12, 1) if calendar_month == 1 else date(calendar_year, calendar_month - 1, 1)
        next_month = date(calendar_year + 1, 1, 1) if calendar_month == 12 else date(calendar_year, calendar_month + 1, 1)

        student_rows = query_db("SELECT id, student_no, name, class_name FROM students ORDER BY class_name, name")

        if request.method == "POST":
            student_id = request.form.get("student_id", "").strip()
            schedule_date = request.form.get("schedule_date", "").strip()
            schedule_slot = request.form.get("schedule_slot", "").strip()
            custom_slot = request.form.get("custom_slot", "").strip()
            title = request.form.get("title", "").strip()
            note = request.form.get("note", "").strip()

            schedule_time = schedule_slot
            if schedule_slot == "직접입력":
                schedule_time = custom_slot

            if not schedule_date or not title:
                flash("상담일과 일정 제목은 필수입니다.")
            elif schedule_slot == "직접입력" and not custom_slot:
                flash("직접입력을 선택한 경우 시간/교시를 입력해 주세요.")
            else:
                execute_db(
                    """
                    INSERT INTO counsel_schedules(student_id, schedule_date, schedule_time, title, note, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'planned', ?)
                    """,
                    (
                        student_id or None,
                        schedule_date,
                        schedule_time or None,
                        title,
                        note,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )
                flash("상담 일정이 등록되었습니다.")
                return redirect(url_for("schedule", date=schedule_date, month=schedule_date[:7]))

        schedules_for_date = query_db(
            """
            SELECT c.id, c.schedule_date, c.schedule_time, c.title, c.note, c.status,
                   s.id AS student_id, s.name AS student_name, s.class_name
            FROM counsel_schedules c
            LEFT JOIN students s ON s.id = c.student_id
            WHERE c.schedule_date = ?
            ORDER BY c.schedule_time ASC, c.id ASC
            """,
            (selected_date,),
        )

        month_rows = query_db(
            """
            SELECT c.id, c.schedule_date, c.schedule_time, c.title, c.status,
                   s.name AS student_name
            FROM counsel_schedules c
            LEFT JOIN students s ON s.id = c.student_id
            WHERE c.schedule_date BETWEEN ? AND ?
            ORDER BY c.schedule_date ASC, c.schedule_time ASC, c.id ASC
            """,
            (first_day_of_month.isoformat(), last_day_of_month.isoformat()),
        )

        month_counts: dict[str, int] = {}
        schedules_by_date: dict[str, list[dict[str, Any]]] = {}
        for row in month_rows:
            day_key = row["schedule_date"]
            month_counts[day_key] = month_counts.get(day_key, 0) + 1
            schedules_by_date.setdefault(day_key, []).append(dict(row))

        cal = Calendar(firstweekday=0)
        calendar_weeks: list[list[dict[str, Any]]] = []
        for week_dates in cal.monthdatescalendar(calendar_year, calendar_month):
            week_items: list[dict[str, Any]] = []
            for day_obj in week_dates:
                day_key = day_obj.isoformat()
                day_schedules = schedules_by_date.get(day_key, [])
                week_items.append(
                    {
                        "date": day_key,
                        "day": day_obj.day,
                        "is_current_month": day_obj.month == calendar_month,
                        "is_selected": day_key == selected_date,
                        "is_today": day_key == datetime.now().date().isoformat(),
                        "schedules": day_schedules[:3],
                        "extra_count": max(0, len(day_schedules) - 3),
                    }
                )
            calendar_weeks.append(week_items)

        upcoming_schedules = query_db(
            """
            SELECT c.id, c.schedule_date, c.schedule_time, c.title, c.status,
                   s.id AS student_id, s.name AS student_name
            FROM counsel_schedules c
            LEFT JOIN students s ON s.id = c.student_id
            WHERE c.status = 'planned' AND c.schedule_date >= ?
            ORDER BY c.schedule_date ASC, c.schedule_time ASC, c.id ASC
            LIMIT 20
            """,
            (datetime.now().date().isoformat(),),
        )

        return render_template(
            "schedule.html",
            students=student_rows,
            selected_date=selected_date,
            selected_month=first_day_of_month.strftime("%Y-%m"),
            month_title=first_day_of_month.strftime("%Y년 %m월"),
            prev_month=prev_month.strftime("%Y-%m"),
            next_month=next_month.strftime("%Y-%m"),
            calendar_weeks=calendar_weeks,
            schedules_for_date=schedules_for_date,
            month_counts=month_counts,
            upcoming_schedules=upcoming_schedules,
        )

    @app.route("/schedule/<int:schedule_id>/done", methods=["POST"])
    def complete_schedule(schedule_id: int):
        execute_db(
            """
            UPDATE counsel_schedules
            SET status = 'done'
            WHERE id = ?
            """,
            (schedule_id,),
        )
        flash("상담 일정이 완료 처리되었습니다.")
        selected_date = request.form.get("date", datetime.now().date().isoformat())
        return redirect(url_for("schedule", date=selected_date, month=selected_date[:7]))

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

            CREATE TABLE IF NOT EXISTS counsel_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                schedule_date TEXT NOT NULL,
                schedule_time TEXT,
                title TEXT NOT NULL,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'planned',
                created_at TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
    conn.close()


def list_backup_files() -> list[Path]:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(BACKUP_DIR.glob("counsel_backup_*.zip"), reverse=True)


def prune_old_backups() -> None:
    backups = list_backup_files()
    for old_file in backups[MAX_BACKUP_FILES:]:
        old_file.unlink(missing_ok=True)


def create_backup_archive(trigger: str = "auto") -> str:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"counsel_backup_{timestamp}_{trigger}.zip"
    backup_path = BACKUP_DIR / backup_name

    with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        if DB_PATH.exists():
            zip_file.write(DB_PATH, arcname="counsel.db")
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.rglob("*"):
                if file_path.is_file():
                    arcname = Path("uploads") / file_path.relative_to(UPLOAD_DIR)
                    zip_file.write(file_path, arcname=str(arcname))

    prune_old_backups()
    return backup_name


def ensure_daily_auto_backup() -> str | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    today = datetime.now().date().isoformat()
    row = conn.execute("SELECT value FROM app_settings WHERE key = 'last_auto_backup_date'").fetchone()
    if row and row["value"] == today:
        conn.close()
        return None

    backup_name = create_backup_archive(trigger="auto")
    conn.execute(
        """
        INSERT INTO app_settings(key, value)
        VALUES ('last_auto_backup_date', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (today,),
    )
    conn.commit()
    conn.close()
    return backup_name


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
    auto_backup = ensure_daily_auto_backup()
    if auto_backup:
        print(f"[INFO] 자동 백업 생성: {auto_backup}")
    app.run(host="0.0.0.0", port=5000, debug=True)
