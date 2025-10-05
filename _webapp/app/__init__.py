from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def _odbc_brace(v: str) -> str:
    # ODBC rule: wrap in {} and double any } inside
    return '{' + v.replace('}', '}}') + '}'


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

    server = os.getenv("DB_SERVER")  # e.g. kicker-automation
    database = os.getenv("DB_NAME")  # e.g. kicker-automation
    username = os.getenv("DB_USER")  # e.g. app_user OR admin@kicker-automation
    password = os.getenv("DB_PASS")  # can include " ; } etc.

    odbc = urllib.parse.quote_plus(
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{server}.database.windows.net,1433;"
        f"Database={database};"
        f"Uid={username};"
        f"Pwd={_odbc_brace(password)};"
        "Encrypt=yes;TrustServerCertificate=no;"
        "Connection Timeout=15"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc:///?odbc_connect={odbc}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True, "pool_recycle": 300}

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .auth import auth_bp
    from .results import results_bp
    from .admin import admin_bp
    from .routes import main_bp
    from .video import video_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(results_bp)

    from .stream_worker import StreamWorker
    # note: 192.168.x.x won't be reachable from Azure; consider a public or VNet-reachable endpoint
    stream_worker = StreamWorker(
        app, rtmp_url="rtmp://192.168.151.16:1935/live/stream")
    stream_worker.start()
    app.stream_worker = stream_worker

    return app
