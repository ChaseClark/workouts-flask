import os
from datetime import datetime
from flask import Flask, g, jsonify

from workouts import exercises, workout_exercises


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "workouts.sqlite"),
    )
    # track uptime of server process
    start = datetime.now()
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/up")
    def up():
        # TODO: test a db call or another sanity check and return "down" if fails
        return jsonify(
            {"status": "ok", "uptimeSeconds": (datetime.now() - start).seconds}
        )

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import workouts

    app.register_blueprint(workouts.bp)
    app.register_blueprint(exercises.bp, url_prefix="/exercises")
    app.register_blueprint(workout_exercises.bp, url_prefix="/workout-exercises")
    app.add_url_rule("/", endpoint="index")

    return app
