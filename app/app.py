from flask import (Flask, jsonify)
from dotenv import load_dotenv
from app.db.base import flask_env
from app.db.session import db
from app.core.security import define_CORS
from app.core.errors import (
    APIError,
    handle_api_error as api_error
)
from app.api import (
    auth_bp,
    video_bp,
    search_bp,
    info_bp,
)

load_dotenv()

def create_app(config_name:str="dev") -> Flask:
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
    db.init_app(app)
    define_CORS(app)

    @app.route("/routes", methods=["GET"])
    def index() -> tuple[dict, int]:
        return jsonify({
            "message": "Welcome to Hypertube API",
            "version": "1.0.0",
            "endpoints": {
                "info": "/api/info",
                "auth": "/api/auth",
                "search": "/api/search",
                "video": "/api/video",
            }
        }), 200

    @app.route("/health", methods=["GET"])
    def health() -> tuple[dict, int]:
        """
        Health check endpoint for Docker healthcheck
        """
        return jsonify({"status": "healthy"}), 200

    app.register_blueprint(info_bp, url_prefix="/api/info")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(video_bp, url_prefix="/api/video")

    app.register_error_handler(APIError, api_error)
    
    return app


from app import app_settings as settings

app: Flask = create_app(settings.get("ENV_NAME", "dev"))

if __name__ == "__main__":
    app.run(
        host=settings.get("API_HOST", "127.0.0.1"),
        port=settings.get("API_PORT", 5000),
        debug=settings.get("DEBUG", False)
    )
