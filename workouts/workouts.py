from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from workouts.auth import login_required
from workouts.db import get_db

bp = Blueprint("workouts", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()
    workouts = db.execute(
        "SELECT p.id, title, notes, created, user_id, username"
        " FROM workout p JOIN user u ON p.user_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("workouts/index.html", workouts=workouts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        notes = request.form["notes"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO workout (title, notes, user_id)" " VALUES (?, ?, ?)",
                (title, notes, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("workouts.index"))

    return render_template("workouts/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    workout = get_workout(id)

    if request.method == "POST":
        title = request.form["title"]
        notes = request.form["notes"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE workout SET title = ?, notes = ?" " WHERE id = ?",
                (title, notes, id),
            )
            db.commit()
            return redirect(url_for("workouts.index"))

    return render_template("workouts/update.html", workout=workout)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_workout(id)
    db = get_db()
    db.execute("DELETE FROM workout WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("workouts.index"))


def get_workout(id, check_user=True):
    workout = (
        get_db()
        .execute(
            "SELECT w.id, title, notes, created, user_id, username"
            " FROM workout w JOIN user u ON w.user_id = u.id"
            " WHERE w.id = ?",
            (id,),
        )
        .fetchone()
    )

    if workout is None:
        abort(404, f"workout id {id} doesn't exist.")

    if check_user and workout["user_id"] != g.user["id"]:
        abort(403)

    return workout
