from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    session,
    url_for,
)
from werkzeug.exceptions import abort

from workouts.auth import login_required
from workouts.db import get_db

bp = Blueprint("workout_exercises", __name__)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    we = get_workout_exercise(id)
    db = get_db()
    db.execute(
        "DELETE FROM workout_exercise WHERE id = ? AND user_id = ?", (id, g.user["id"])
    )
    db.commit()
    # workout_exercises = db.execute(
    #     " SELECT workout_exercise.id, workout_exercise.user_id, workout_id, exercise_id, sets, reps, weight, exercise.id, name"
    #     " FROM workout_exercise"
    #     " INNER JOIN exercise ON workout_exercise.exercise_id = exercise.id"
    #     " WHERE workout_exercise.user_id = ? AND workout_id = ?"
    #     " ORDER BY workout_exercise.id",
    #     (g.user["id"], we["workout_id"]),
    # ).fetchall()
    return redirect(url_for("workouts.detail", id=session["workout_id"]))


def get_workout_exercise(id):
    we = (
        get_db()
        .execute(
            "SELECT id, user_id, workout_id, exercise_id, sets, reps, weight"
            " FROM workout_exercise"
            " WHERE id = ? AND user_id = ?",
            (id, g.user["id"]),
        )
        .fetchone()
    )
    if we is None:
        abort(404, f"workout exercise id {id} doesn't exist.")

    return we
