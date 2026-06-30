import os
import atexit
import logging
from flask import Flask, render_template, send_from_directory, Blueprint, request, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes import config_bp, generator_bp, scheduler_bp, linkedin_bp, dashboard_bp, connection_bp
from services import get_scheduler

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
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(connection_bp)
    
    with app.app_context():
        scheduler = get_scheduler(app)
    
    # Register shutdown handler
    def shutdown_scheduler():
        if scheduler and scheduler.scheduler:
            scheduler.shutdown()
    atexit.register(shutdown_scheduler)
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'code': 404,
                'message': 'Endpoint not found',
                'data': None
            }), 404
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}', exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                'code': 500,
                'message': 'Internal server error',
                'data': None
            }), 500
        return 'Internal Server Error', 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f'Unexpected error: {error}', exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                'code': 500,
                'message': 'Internal server error',
                'data': None
            }), 500
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

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
