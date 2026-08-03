from flask import Blueprint, redirect, url_for, session, request, render_template
from core import build_auth_flow, complete_auth_flow

bp = Blueprint("auth", __name__)


@bp.route("/login")
def login():
    flow = build_auth_flow(redirect_uri=url_for("auth.authorized", _external=True))
    session["flow"] = flow
    return redirect(flow["auth_uri"])


@bp.route("/getAToken")
def authorized():
    result = complete_auth_flow(session.get("flow", {}), request.args)
    if "error" in result:
        return render_template("index.html", user=None, error=result.get("error_description"))
    session["user"] = result.get("id_token_claims")
    return redirect(url_for("main.index"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))