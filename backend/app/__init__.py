from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS
from app.api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints first
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint (accessible at /health - simpler path)
    @app.route('/health')
    def health_check():
        """Health check endpoint for Railway"""
        return jsonify({'status': 'healthy', 'message': 'Privacy-Preserving Query API is running'})
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Privacy-Preserving Query API',
            'version': '1.0',
            'endpoints': {
                'health': '/health',
                'docs': '/swagger',
                'upload': '/api/upload/',
                'schema': '/api/schema/',
                'query': '/api/query/'
            }
        })
    
    return app 