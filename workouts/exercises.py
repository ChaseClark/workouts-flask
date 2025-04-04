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

bp = Blueprint("exercises", __name__)


@bp.route(
    "/create",
    methods=("POST",),
)
@login_required
def create():
    id = session["workout_id"]
    name = request.form["exerciseName"]
    category_id = request.form["category"]
    error = None
    if not name:
        error = "Exercise name is required."
    if error is None:
        try:
            db = get_db()
            db.execute(
                "INSERT INTO exercise (name, category_id, user_id)" " VALUES (?, ?, ?)",
                (name, category_id, g.user["id"]),
            )
            db.commit()
        except db.IntegrityError:
            error = f"Exercise: '{name}' already exists."
            flash(error)
        return redirect(url_for("workouts.detail", id=id))
    else:
        flash(error)
