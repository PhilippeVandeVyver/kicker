from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user
from .models import Admins, Game, Player, GamePlayer
from .video import video_feed
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .stream_worker import StreamWorker
from flask import current_app
import threading
import time

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
def dashboard():

    players = Player.query.all()
    return render_template("admin_dashboard.html", players= players)

@admin_bp.route("/start_game", methods=["POST"])
@login_required
def start_game():

    slot1 = request.form.get("slot1")
    slot2 = request.form.get("slot2")
    slot3 = request.form.get("slot3")
    slot4 = request.form.get("slot4")  # list of user IDs
    selected_slots = [slot1, slot2, slot3, slot4]
    if not slot1 and not slot2 and not slot3 and not slot4:
        flash("Select at least one player")
        return redirect(url_for("admin.dashboard"))

    # Start stream/game worker for selected players
    game = Game()
    db.session.add(game)
    db.session.commit()
    app = current_app._get_current_object()

    slot_names = ["Team1_Player1", "Team1_Player2", "Team2_Player1", "Team2_Player2"]
    for slot_name, player_id in zip(slot_names, selected_slots):
        if player_id:
            link = GamePlayer(
                GameId=game.GameId,
                PlayerId=int(player_id),
                slot=slot_name
            )
            db.session.add(link)

    db.session.commit()  # save all links
    current_app.stream_worker.start_processing(game.GameId)
    flash("Game started!")
    def auto_stop():
        time.sleep(5 * 60)  # 5 minutes in seconds
        with app.app_context():  # ensure Flask context
            app.stream_worker.stop_processing()
            print("Game automatically stopped after 5 minutes.")
    threading.Thread(target=auto_stop, daemon=True).start()
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/stop_game")
@login_required
def stop_game():
    with current_app.app_context():
        current_app.stream_worker.stop_processing()
    flash("Game stopped!")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Admins.query.filter_by(Email=email).first()

        if not user or not check_password_hash(user.PasswordHash, password):
            flash("Invalid login!")
            return redirect(url_for("admin.login"))

        login_user(user)
        return redirect(url_for("admin.dashboard"))

    return render_template("login.html")

@admin_bp.route("/innit")
@login_required
def innit():

    print("hello")
    flash("Stream worker started!")
    return redirect(url_for("admin.dashboard"))
 
@admin_bp.route("/stop_all")
@login_required
def stop_all():

    current_app.stream_worker.stop()
    flash("Stream worker stopped!")
    return redirect(url_for("admin.dashboard"))