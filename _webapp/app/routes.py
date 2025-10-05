from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html",emailexists = False)
@main_bp.route("/registered")
def registered_check():
    return render_template("registered.html")