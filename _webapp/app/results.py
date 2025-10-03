from flask import Blueprint, render_template, request
from .models import Player

results_bp = Blueprint("results", __name__)

@results_bp.route("/results")
def search():
    email = request.args.get("email")
    print(email)
    player = None
    games = []
    if email:
        player = Player.query.filter_by(Email=email).first()
        if player:
            games = player.games
    return render_template("results.html", player=player, games=games,email=email)
    
