from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from werkzeug.datastructures import FileStorage
import logging
from app.utils.data_loader import data_loader
from app.core.query_engine import query_engine

# Create blueprint
api_bp = Blueprint('api', __name__)
api = Api(api_bp, title='Privacy-Preserving Query API', version='1.0', description='Stata-style interface for safe frequency tables')

# Create namespaces
upload_ns = api.namespace('upload', description='Dataset upload operations')
schema_ns = api.namespace('schema', description='Dataset schema operations')
query_ns = api.namespace('query', description='Query execution operations')

# Define models for API documentation
upload_model = api.model('UploadResponse', {
    'dataset_key': fields.String(required=True, description='Unique identifier for the uploaded dataset'),
    'row_count': fields.Integer(required=True, description='Number of rows in the dataset'),
    'column_count': fields.Integer(required=True, description='Number of columns in the dataset')
})

column_model = api.model('Column', {
    'name': fields.String(required=True, description='Column name'),
    'type': fields.String(required=True, description='Data type (string or numeric)'),
    'unique_values': fields.Integer(required=True, description='Number of unique values')
})

schema_model = api.model('SchemaResponse', {
    'columns': fields.List(fields.Nested(column_model), required=True, description='List of columns'),
    'row_count': fields.Integer(required=True, description='Number of rows in the dataset'),
    'dataset_key': fields.String(required=True, description='Dataset identifier')
})

query_request_model = api.model('QueryRequest', {
    'dataset_key': fields.String(required=True, description='Dataset identifier'),
    'command': fields.String(required=True, description='Stata-style command (e.g., "tab sex age if region == \'Rural\'")')
})

query_response_model = api.model('QueryResponse', {
    'columns': fields.List(fields.String, required=True, description='Column names'),
    'data': fields.List(fields.List(fields.Raw), required=True, description='Query results'),
    'row_count': fields.Integer(required=True, description='Number of rows in filtered dataset'),
    'command': fields.String(required=True, description='Executed command')
})

# File upload parser
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='CSV file to upload')

# Query parser
query_parser = api.parser()
query_parser.add_argument('dataset_key', type=str, required=True, help='Dataset identifier')
query_parser.add_argument('command', type=str, required=True, help='Stata-style command')

@upload_ns.route('/')
class UploadResource(Resource):
    @api.expect(upload_parser)
    @api.marshal_with(upload_model, code=201)
    @api.doc(description='Upload a CSV dataset (max 1GB)')
    def post(self):
        """Upload a CSV dataset"""
        try:
            args = upload_parser.parse_args()
            file = args['file']
            
            if not file:
                api.abort(400, 'No file provided')
            
            # Upload and process the dataset
            result = data_loader.upload_dataset(file)
            
            return result, 201
            
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            api.abort(500, 'Internal server error')

@schema_ns.route('/')
class SchemaResource(Resource):
    @api.doc(description='Get dataset schema information', params={'dataset_key': 'Dataset identifier'})
    @api.marshal_with(schema_model)
    def get(self):
        """Get dataset schema"""
        try:
            dataset_key = request.args.get('dataset_key')
            
            if not dataset_key:
                api.abort(400, 'dataset_key parameter is required')
            
            # Get schema information
            schema = data_loader.get_schema(dataset_key)
            
            return schema
            
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            logging.error(f"Schema error: {str(e)}")
            api.abort(500, 'Internal server error')

@query_ns.route('/')
class QueryResource(Resource):
    @api.expect(query_request_model)
    @api.marshal_with(query_response_model)
    @api.doc(description='Execute a Stata-style query with privacy protection')
    def post(self):
        """Execute a privacy-preserving query"""
        try:
            data = request.get_json()
            
            if not data:
                api.abort(400, 'No JSON data provided')
            
            dataset_key = data.get('dataset_key')
            command = data.get('command')
            privacy_mode = data.get('privacy_mode', 'suppression')
            
            print(f"DEBUG API: Received privacy_mode: {privacy_mode}")
            print(f"DEBUG API: privacy_mode type: {type(privacy_mode)}")
            print(f"DEBUG API: Full request data: {data}")
            
            if not dataset_key or not command:
                api.abort(400, 'dataset_key and command are required')
            
            # Validate privacy mode
            if privacy_mode not in ['suppression', 'differential_privacy']:
                api.abort(400, 'privacy_mode must be either "suppression" or "differential_privacy"')
            
            # Load dataset
            df = data_loader.get_dataset(dataset_key)
            print(f"=== DATASET INFO ===")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            print(f"===================")
            logging.info(f"Loaded dataset with columns: {df.columns.tolist()}")
            logging.info(f"Dataset shape: {df.shape}")
            
            # Execute query with privacy mode
            print(f"DEBUG API: About to call query_engine.execute_query with privacy_mode: {privacy_mode}")
            result = query_engine.execute_query(df, command, privacy_mode)
            print(f"DEBUG API: Query engine returned result")
            
            return result
            
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            logging.error(f"Query error: {str(e)}")
            api.abort(500, 'Internal server error')

@api_bp.route('/load-demo/', methods=['POST'])
def load_demo_dataset():
    """Load the synthetic injuries demo dataset for demonstration purposes."""
    try:
        result = data_loader.load_demo_injuries_dataset()
        return jsonify(result), 201
    except Exception as e:
        logging.error(f"Demo dataset load error: {str(e)}")
        return jsonify({'message': str(e)}), 500 