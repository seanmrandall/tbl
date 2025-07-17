from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS
from app.api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure API
    api = Api(app, 
              title='Privacy-Preserving Query API',
              description='A Stata-style interface for safe frequency tables',
              version='1.0',
              doc='/swagger')
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint (accessible at /api/health)
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for Railway"""
        return jsonify({'status': 'healthy', 'message': 'Privacy-Preserving Query API is running'})
    
    return app 