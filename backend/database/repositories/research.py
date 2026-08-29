from __future__ import annotations

from database.connection import get_connection


def record_task_log(task: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO task_logs (task_id, condition, user_id, completed, duration_ms, voice_used, error) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                task.get("task_id"),
                task.get("condition"),
                task.get("user_id"),
                1 if task.get("completed") else 0,
                task.get("duration_ms"),
                1 if task.get("voice_used") else 0,
                task.get("error"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def record_survey_response(survey: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO survey_responses (task_id, condition, user_id, comprehension_score, trust_score, sus_score, feedback) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                survey.get("task_id"),
                survey.get("condition"),
                survey.get("user_id"),
                survey.get("comprehension_score"),
                survey.get("trust_score"),
                survey.get("sus_score"),
                survey.get("feedback"),
            ),
        )
        conn.commit()
    finally:
        conn.close()
