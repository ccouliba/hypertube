import os
from flask import (Flask, jsonify)
from flask_smorest import Api
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from app.db.base import flask_env
from app.db.session import db
from app.core.configs import APP_CONFIG
from app.core.security import (define_CORS, limiter)
from app.core.errors import (
    APIError,
    handle_api_error as api_error,
    handle_http_exception as http_error,
    handle_unhandled_exception as unhandled_error,
)
from app.api import (
    auth_bp,
    video_bp,
    search_bp,
    info_bp,
)

load_dotenv()

def create_app(config_name: str = "dev") -> Flask:
    """
    Application Factory Pattern
    Create and configure the Flask application
    Args:
        config_name: Configuration name (development, production, etc.)
    Returns:
        Flask app instance
    """

    app: Flask = Flask(__name__)
    app.config.from_object(flask_env.get(config_name, flask_env["default"]))
    
    # OpenAPI / Swagger
    _oa = APP_CONFIG["openapi"]
    app.config["API_TITLE"] = _oa["title"]
    app.config["API_VERSION"] = _oa["version"]
    app.config["OPENAPI_VERSION"] = _oa["openapi_version"]
    app.config["OPENAPI_URL_PREFIX"] = _oa["url_prefix"]
    app.config["OPENAPI_SWAGGER_UI_PATH"] = _oa["swagger_ui_path"]
    app.config["OPENAPI_SWAGGER_UI_URL"] = _oa["swagger_ui_url"]
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": _oa["api_type"],
                    "scheme": _oa["token_schemes"],
                    "bearerFormat": _oa["bearer_format"],
                }
            }
        }
    }

    _migrations_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "migrations")
    db.init_app(app)
    Migrate(app, db, directory=_migrations_dir)
    define_CORS(app)
    limiter.init_app(app)

    # Built-in routes
    @app.route("/health", methods=["GET"])
    def health() -> tuple[dict, int]:
        """Health check endpoint for Docker healthcheck"""
        return jsonify({"status": "healthy"}), 200

    # Blueprints (flask-smorest)
    api: Api = Api(app)
    api.register_blueprint(info_bp, url_prefix="/api/info")
    api.register_blueprint(auth_bp, url_prefix="/api/auth")
    api.register_blueprint(search_bp, url_prefix="/api/search")
    api.register_blueprint(video_bp, url_prefix="/api/video")

    app.register_error_handler(APIError, api_error)
    app.register_error_handler(HTTPException, http_error)
    app.register_error_handler(Exception, unhandled_error)

    return app


app: Flask = create_app(APP_CONFIG["app"]["env"])


if __name__ == "__main__":
    app.run(
        host=APP_CONFIG["api"]["host"],
        port=APP_CONFIG["api"]["port"],
        debug=APP_CONFIG["debug"]
    )
