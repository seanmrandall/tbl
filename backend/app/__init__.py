from flask import Flask, jsonify, send_from_directory
from flask_restx import Api
from flask_cors import CORS
from app.api.routes import api_bp
import os

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints first
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint (accessible at /health - simpler path)
    @app.route('/health')
    def health_check():
        """Health check endpoint for Railway"""
        return jsonify({'status': 'healthy', 'message': 'Privacy-Preserving Query API is running'})
    
    # Root endpoint - serve frontend
    @app.route('/')
    def root():
        """Serve the frontend application"""
        return send_from_directory(app.static_folder, 'index.html')
    
    # Catch-all route for frontend routing
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve frontend static files"""
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            # For client-side routing, serve index.html
            return send_from_directory(app.static_folder, 'index.html')
    
    return app 