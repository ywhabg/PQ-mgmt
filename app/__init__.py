import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app(config_name="production"):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    jwt.init_app(app)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app
    
 
