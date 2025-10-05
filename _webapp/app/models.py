from . import db
from sqlalchemy.orm import relationship
import datetime

class GamePlayer(db.Model):
    __tablename__ = "GamePlayers"

    GameId = db.Column(db.Integer, db.ForeignKey("Game.GameId"), primary_key=True)
    PlayerId = db.Column(db.Integer, db.ForeignKey("Player.PlayerId"), primary_key=True)
    slot = db.Column(db.String(20), nullable=False)  
    # Examples: "Team1-P1", "Team1-P2", "Team2-P1", "Team2-P2"

    # Relationships
    player = db.relationship("Player", back_populates="game_links")
    game = db.relationship("Game", back_populates="player_links")


class Player(db.Model):
    __tablename__ = "Player"
    PlayerId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(500),  nullable=True)
    LastName= db.Column(db.String(500), nullable=True)
    Email = db.Column(db.String(500),  nullable=True)
    CompanyName = db.Column(db.String(500), nullable=True)
    ContactButton = db.Column(db.Boolean, nullable = True)
    # Link through GamePlayer
    game_links = db.relationship("GamePlayer", back_populates="player")

    # Convenience shortcut (all games, no slot info)
    @property
    def games(self):
        return [link.game for link in self.game_links]



class Game(db.Model):
    __tablename__ = "Game"
    GameId = db.Column(db.Integer, primary_key=True)
    GameSettingId = db.Column(db.Integer, default=1)
    StartDateTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    EndDateTime = db.Column(db.Integer,default=datetime.datetime.utcnow)
    Score_Team_1 = db.Column(db.Integer,default=0)
    Score_Team_2 = db.Column(db.Integer,default=0)
    Calculated_Points_Team_1 = db.Column(db.Integer,default=0)
    Calculated_Points_Team_2 = db.Column(db.Integer,default=0)
    # Link through GamePlayer
    player_links = db.relationship("GamePlayer", back_populates="game")

    # Convenience shortcut (all players, no slot info)
    @property
    def players(self):
        return [link.player for link in self.player_links]
    heatmap = db.relationship("Heatmaps", back_populates="game_heatmap", uselist=False)

class Heatmaps(db.Model):
    __tablename__ =  "Heatmaps"
    id = db.Column(db.Integer, primary_key=True)
    gameId = db.Column(db.Integer,db.ForeignKey("Game.GameId"))
    Heatmap_Url = db.Column(db.String(500),nullable=True)
    game_heatmap = db.relationship("Game", back_populates="heatmap")


