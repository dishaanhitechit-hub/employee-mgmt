import os
from datetime import timedelta

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import config
from extensions import db

import models  # noqa: F401

from routes.auth_routes         import bp as auth_bp
from routes.organization_routes import bp as org_bp
from routes.user_routes         import bp as user_bp
from routes.role_routes         import bp as role_bp
from routes.permission_routes   import bp as perm_bp
from routes.employee_routes     import bp as emp_bp
from routes.department_routes   import bp as dept_bp
from routes.stats_routes                import bp as stats_bp
from routes.employee_permission_routes  import bp as emp_perm_bp
from routes.attendance_routes           import bp as attendance_bp

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def create_app() -> Flask:
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

    app.config["SQLALCHEMY_DATABASE_URI"]        = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SQLALCHEMY_ECHO"]                = config.SQLALCHEMY_ECHO
    app.config["JWT_SECRET_KEY"]                 = config.JWT_SECRET
    app.config["JWT_ACCESS_TOKEN_EXPIRES"]       = timedelta(minutes=config.JWT_ACCESS_EX)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"]      = timedelta(days=config.JWT_REFRESH_EX)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    app.register_blueprint(auth_bp,   url_prefix="/api/auth")
    app.register_blueprint(org_bp,    url_prefix="/api/organizations")
    app.register_blueprint(user_bp,   url_prefix="/api/users")
    app.register_blueprint(role_bp,   url_prefix="/api/roles")
    app.register_blueprint(perm_bp,   url_prefix="/api/permissions")
    app.register_blueprint(emp_bp,    url_prefix="/api/employees")
    app.register_blueprint(dept_bp,   url_prefix="/api/departments")
    app.register_blueprint(stats_bp,     url_prefix="/api/stats")
    app.register_blueprint(emp_perm_bp,   url_prefix="/api/employee-permissions")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        target = os.path.join(FRONTEND_DIR, path)
        if path and os.path.exists(target):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=config.PORT)
