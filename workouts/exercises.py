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

bp = Blueprint("exercises", __name__)


@bp.route(
    "/create",
    methods=("POST",),
)
@login_required
def create():
    name = request.form["name"]
    if not name:
        error = "Exercise name is required."
    error = None
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            "INSERT INTO exercise (name, user_id)" " VALUES (?, ?)",
            (name, g.user["id"]),
        )
        db.commit()
        return "ok"
