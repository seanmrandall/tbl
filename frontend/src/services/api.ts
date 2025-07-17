import axios from 'axios';
import { 
  UploadResponse, 
  SchemaResponse, 
  QueryRequest, 
  QueryResponse, 
  ApiError 
} from '../types/api';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    console.error('Response data:', error.response?.data);
    console.error('Response status:', error.response?.status);
    
    let errorMessage = 'An error occurred';
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.response?.data) {
      errorMessage = typeof error.response.data === 'string' 
        ? error.response.data 
        : JSON.stringify(error.response.data);
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    const apiError: ApiError = {
      message: errorMessage,
      status: error.response?.status,
    };
    return Promise.reject(apiError);
  }
);

export const uploadDataset = async (file: File, delimiter: string = 'comma'): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('delimiter', delimiter);
  
  const response = await api.post<UploadResponse>('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getSchema = async (datasetKey: string): Promise<SchemaResponse> => {
  const response = await api.get<SchemaResponse>('/schema/', {
    params: { dataset_key: datasetKey },
  });
  
  return response.data;
};

export const executeQuery = async (request: QueryRequest): Promise<QueryResponse> => {
  console.log('Sending query request:', request);
  const response = await api.post<QueryResponse>('/query/', request);
  
  return response.data;
};

export const healthCheck = async (): Promise<{ status: string; message: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api; 