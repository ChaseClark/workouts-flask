from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
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
        " ORDER BY created DESC"
        " LIMIT 15",
        (id,),
    ).fetchall()
    return render_template("workouts/index.html", workouts=workouts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        notes = request.form["notes"]
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO workout (notes, user_id)" " VALUES (?, ?)",
                (notes, g.user["id"]),
            )
            last_id = cursor.lastrowid
            db.commit()
            # redirect to update so that user can add exercises to workout
            return redirect(url_for("workouts.update", id=last_id))

    return render_template("workouts/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    workout = get_workout(id)

    if request.method == "POST":
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
