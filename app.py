import os
import logging
from flask import Flask, render_template, send_from_directory, Blueprint
from flask_cors import CORS
from config import Config
from database import init_db
from config_bp import config_bp
from generator_bp import generator_bp
from scheduler_bp import scheduler_bp
from linkedin_bp import linkedin_bp
from scheduler import get_scheduler

def setup_logging(app):
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    app.logger.setLevel(log_level)

def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'),
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend/pages')
    )
    
    app.config.from_object(config_class)
    
    setup_logging(app)
    
    CORS(app, supports_credentials=True)
    
    init_db(app)
    
    main_bp = create_main_blueprint()
    app.register_blueprint(main_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(generator_bp)
    app.register_blueprint(scheduler_bp)
    app.register_blueprint(linkedin_bp)
    
    with app.app_context():
        scheduler = get_scheduler(app)
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return 'Internal Server Error', 500
    
    return app

def create_main_blueprint():
    bp = Blueprint('main', __name__)
    
    @bp.route('/')
    def index():
        return render_template('index.html')
    
    @bp.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @bp.route('/connections')
    def connections():
        return render_template('connections.html')
    
    @bp.route('/posting')
    def posting():
        return render_template('posting.html')
    
    @bp.route('/logs')
    def logs():
        return render_template('logs.html')
    
    @bp.route('/settings')
    def settings():
        return render_template('settings.html')
    
    @bp.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'), filename)
    
    return bp

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
