from flask import Flask
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
    
    return app 