from datetime import datetime
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import abort

from workouts.auth import login_required
from workouts.db import get_db

bp = Blueprint("workouts", __name__)


@bp.route("/")
@login_required
def index():
    id = g.user["id"]
    db = get_db()
    workouts = db.execute(
        "SELECT id, notes, created, user_id"
        " FROM workout"
        " WHERE user_id = ?"
        " ORDER BY created DESC, id"
        " LIMIT 15",
        (id,),
    ).fetchall()

    return render_template(
        "workouts/index.html",
        workouts=workouts,
    )


@bp.route("/create", methods=("POST",))
@login_required
def create():
    if request.method == "POST":
        db = get_db()

        time = request.form["time"]
        dt = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        sqlite_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.execute(
            "INSERT INTO workout (notes, user_id, created) VALUES (?, ?, ?)",
            ("", g.user["id"], sqlite_time),
        )
        last_id = cursor.lastrowid
        db.commit()
        return redirect(url_for("workouts.detail", id=last_id))


@bp.route("/<int:id>", methods=("GET",))
@login_required
def detail(id):
    workout = get_workout(id)
    session["workout_id"] = id
    if request.method == "GET":
        db = get_db()
        exercises = db.execute(
            " SELECT id, name, category_id, user_id"
            " FROM exercise"
            " WHERE user_id = ?"
            " ORDER BY name",
            (g.user["id"],),
        ).fetchall()
        workout_exercises = db.execute(
            " SELECT workout_exercise.id, workout_exercise.user_id, workout_id, exercise_id, sets, reps, weight, exercise.id, name"
            " FROM workout_exercise"
            " INNER JOIN exercise ON workout_exercise.exercise_id = exercise.id"
            " WHERE workout_exercise.user_id = ? AND workout_id = ?"
            " ORDER BY workout_exercise.id",
            (g.user["id"], id),
        ).fetchall()
        return render_template(
            "workouts/detail.html",
            workout=workout,
            categories=g.categories,
            exercises=exercises,
            workout_exercises=workout_exercises,
            id=id,
        )


@bp.route("/<int:id>/add-exercise", methods=("POST",))
@login_required
def add_exercise(id):
    db = get_db()
    exercise = request.form["select_exercise"]
    sets = request.form["sets"]
    reps = request.form["reps"]
    weight = request.form["weight"]
    print(f"{exercise=} {sets=} {reps=} {weight=}")
    db.execute(
        "INSERT INTO workout_exercise (user_id, workout_id, exercise_id, sets, reps, weight)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (g.user["id"], id, exercise, sets, reps, weight),
    )
    db.commit()
    return redirect(url_for("workouts.detail", id=id))


@bp.route("/<int:id>/notes/edit", methods=("GET", "PUT"))
@login_required
def notes_edit(id):
    workout = get_workout(id)
    if request.method == "PUT":
        notes = request.form["notes"]
        error = None
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE workout SET notes = ?" " WHERE id = ?",
                (notes, id),
            )
            db.commit()
            return render_template("workouts/partials/notes.html", workout=workout)
    return render_template("workouts/partials/edit_notes.html", workout=workout)


@bp.route("/<int:id>/notes", methods=("GET",))
@login_required
def notes(id):
    workout = get_workout(id)
    return render_template("workouts/partials/notes.html", workout=workout)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    db = get_db()
    db.execute("DELETE FROM workout WHERE id = ? AND user_id = ?", (id, g.user["id"]))
    db.commit()
    return redirect(url_for("workouts.index"))


def get_workout(id, check_user=True):
    workout = (
        get_db()
        .execute(
            "SELECT id, notes, created, user_id"
            " FROM workout"
            " WHERE id = ? AND user_id = ?",
            (id, g.user["id"]),
        )
        .fetchone()
    )

    if workout is None:
        abort(404, f"workout id {id} doesn't exist.")

    if check_user and workout["user_id"] != g.user["id"]:
        abort(403)

    return workout


def get_exercise(id):
    exercise = (
        get_db()
        .execute(
            "SELECT id, user_id, category_id, name"
            " FROM exercise"
            " WHERE id = ? AND user_id = ?",
            (id, g.user["id"]),
        )
        .fetchone()
    )

    if exercise is None:
        abort(404, f"workout id {id} doesn't exist.")

    return exercise
