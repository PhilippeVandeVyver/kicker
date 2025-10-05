from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.parse
db = SQLAlchemy()


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
        f"Pwd={password};"
        "Encrypt=yes;TrustServerCertificate=no;"
        "Connection Timeout=15"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc:///?odbc_connect={odbc}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True, "pool_recycle": 300}

    db.init_app(app)


    from .auth import auth_bp
    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
