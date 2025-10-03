from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Admins , Player

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
            flash("Email already exists")
            return redirect(url_for("auth.register"))

        new_player = Player(
            FirstName=firstname,
            LastName=lastname,
            Email=email,
            CompanyName = company,
        )
        db.session.add(new_player)
        db.session.commit()
        flash("Account created!")
        return redirect(url_for("main.index"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Admins.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid login")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("admin.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
