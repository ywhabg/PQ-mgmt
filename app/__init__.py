import logging
import os
import sys

from flask import Flask, jsonify
from sqlalchemy import text

from app.extensions import db, jwt, cors, migrate, redis_client
from config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"], logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    db.init_app(app)
    jwt.init_app(app)

    cors.init_app(
        app,
        origins=app.config["CORS_ORIGINS"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    migrate.init_app(app, db)
    redis_client.init_app(app)

    from app.routes.auth import bp as auth_bp
    from app.routes.pq import bp as pq_bp
    from app.routes.ai import bp as ai_bp
    from app.routes.rag import bp as rag_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.workflow import bp as workflow_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pq_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(workflow_bp)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify(
            {
                "name": "DPQMS API",
                "version": "1.0.0",
                "status": "running",
                "environment": config_name,
            }
        ), 200

    @app.route("/health", methods=["GET"])
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(
                {
                    "status": "healthy",
                    "database": "connected",
                    "environment": config_name,
                }
            ), 200
        except Exception as e:
            logging.exception("Health check failed")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(_error):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(_error):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(500)
    def internal_error(error):
        logging.exception(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    return app
