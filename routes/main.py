from flask import Blueprint, session, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", user=session.get("user"))