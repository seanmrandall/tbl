export interface UploadResponse {
  dataset_key: string;
  row_count: number;
  column_count: number;
}

export interface Column {
  name: string;
  type: 'string' | 'numeric';
  unique_values: number;
}

export interface SchemaResponse {
  columns: Column[];
  row_count: number;
  dataset_key: string;
}

export interface QueryRequest {
  dataset_key: string;
  command: string;
  privacy_mode?: 'suppression' | 'differential_privacy';
}

export interface QueryResponse {
  columns: string[];
  data: any[][];
  row_count: number;
  command: string;
  message?: string;
}

export interface ApiError {
  message: string;
  status?: number;
} 