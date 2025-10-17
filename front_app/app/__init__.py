from flask import Flask
from app.config import Config
from app.routes import auth_bp, dashboard_bp, account_bp, api_bp, pages_bp
from app.utils.date_utils import setup_jinja_filters

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)
    
    # Setup Jinja filters
    setup_jinja_filters(app)
    
    return app