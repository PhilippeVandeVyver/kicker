from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import Player

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        company = request.form["company"]

        player = Player.query.filter_by(Email=email).first()
        if player:
            return redirect(url_for("main.index",emailexists = True))

        new_player = Player(
            FirstName=firstname,
            LastName=lastname,
            Email=email,
            CompanyName = company,
        )
        db.session.add(new_player)
        db.session.commit()
        flash("Account created!")
        return redirect(url_for("main.registered_check"))

    return redirect(url_for("main.index",emailexists = False))

