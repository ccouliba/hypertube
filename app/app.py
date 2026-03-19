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
    MIGRATIONS_DIR: str = os.path.join(os.path.dirname(__file__), "migrations")
# os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "migrations")

    def _validate_config(config: dict) -> None:
        """Validate that all required OpenAPI config keys are present"""
        required_keys = [
            "title",
            "version",
            "openapi_version",
            "url_prefix",
            "swagger_ui_path",
            "swagger_ui_url",
            "api_type",
            "token_schemes",
            "bearer_format"
        ]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing OpenAPI config keys: {', '.join(missing_keys)}")

    def _load_open_api_config(config: dict) -> None:
        _validate_config(config)
        app.config["API_TITLE"] = config["title"]
        app.config["API_VERSION"] = config["version"]
        app.config["OPENAPI_VERSION"] = config["openapi_version"]
        app.config["OPENAPI_URL_PREFIX"] = config["url_prefix"]
        app.config["OPENAPI_SWAGGER_UI_PATH"] = config["swagger_ui_path"]
        app.config["OPENAPI_SWAGGER_UI_URL"] = config["swagger_ui_url"]
        app.config["API_SPEC_OPTIONS"] = {
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": config["api_type"],
                        "scheme": config["token_schemes"],
                        "bearerFormat": config["bearer_format"],
                    }
                }
            }
        }
    
    def _register_blueprints(api: Api) -> None:
        """Define and register API blueprints via flask-smorest"""
        api.register_blueprint(info_bp, url_prefix="/api/info")
        api.register_blueprint(auth_bp, url_prefix="/api/auth")
        api.register_blueprint(search_bp, url_prefix="/api/search")
        api.register_blueprint(video_bp, url_prefix="/api/video")

    def _register_error_handlers(app: Flask) -> None:
        """Define and register global error handlers"""
        app.register_error_handler(APIError, api_error)
        app.register_error_handler(HTTPException, http_error)
        app.register_error_handler(Exception, unhandled_error)


    @app.route("/health", methods=["GET"])
    def health() -> tuple[dict, int]:
        """Health check endpoint for Docker healthcheck"""
        return jsonify({"status": "healthy"}), 200


    app: Flask = Flask(__name__)
    app.config.from_object(flask_env.get(config_name, flask_env["default"]))
    _oa: dict = APP_CONFIG["openapi"]
    _load_open_api_config(_oa)
    _migrations_dir: str = MIGRATIONS_DIR
    db.init_app(app)
    Migrate(app, db, directory=_migrations_dir)
    define_CORS(app)
    limiter.init_app(app)
    api: Api = Api(app)
    _register_blueprints(api)
    _register_error_handlers(app)
    return app


if __name__ == "__main__":
    app: Flask = create_app(APP_CONFIG["app"]["env"])
    app.run(
        host=APP_CONFIG["api"]["host"],
        port=APP_CONFIG["api"]["port"],
        debug=APP_CONFIG["debug"]
    )
