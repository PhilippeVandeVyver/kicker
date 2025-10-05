from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

    # Azure SQL connection
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    ).format(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        server=os.getenv("DB_SERVER"),
        database=os.getenv("DB_NAME"),
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import blueprints
    from .auth import auth_bp
    from .routes import main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
