# Privacy-Preserving Query Interface

A web-based, Stata-style interface for safe frequency tables on structured datasets with privacy protection through count suppression.

## Features

- **Stata-style REPL**: Monaco Editor for command input
- **Privacy Protection**: Automatic suppression of counts <5 with complementary rules
- **Variable Sidebar**: Browse available columns and data types
- **Results Table**: Display query results with suppressed values highlighted
- **File Upload**: Support for CSV files up to 1GB
- **Real-time Querying**: Fast execution on large datasets

## Architecture

```
┌──────────────────────────────────────────── Browser ─────────────────────────────────────────────┐
│  • Monaco editor (REPL) • Variable sidebar • Results pane (HTML table)                           │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
        ▲  HTTPS (JSON)                                                               
        ▼
┌─────────────────────────── Flask + Gunicorn container ────────────────────────────┐
│ • DataLoader - CSV upload and pickle caching                                      │
│ • StataParser - Lark grammar for command parsing                                  │
│ • SuppressionEngine - <5 rule + complementary suppression                        │
│ • QueryEngine - Execute filtered cross-tabulations                               │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Frontend**: React 18 + TypeScript, Vite, Chakra UI, Monaco Editor
- **Backend**: Flask 3.0 + Flask-RESTX, Pandas 2.2, Lark parser
- **Deployment**: Docker, Gunicorn

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application:**
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`
   - API documentation: `http://localhost:5000/swagger`
   - Health check: `http://localhost:5000/api/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Docker Setup (Alternative)

1. **Build and run backend:**
   ```bash
   cd backend
   docker build -t pp-query-backend .
   docker run -p 5000:5000 pp-query-backend
   ```

2. **Build and run frontend:**
   ```bash
   cd frontend
   docker build -t pp-query-frontend .
   docker run -p 3000:3000 pp-query-frontend
   ```

## Usage

### 1. Upload Dataset

- Click "Select File" or drag-and-drop a CSV file
- Maximum file size: 1GB
- File must have a header row
- Supported data types: string and numeric

### 2. Browse Variables

- View available columns in the sidebar
- See data types and unique value counts
- Click variables to insert them into queries

### 3. Execute Queries

Use Stata-style commands:

```stata
# One-way frequency table
tab sex

# Two-way cross-tabulation
tab sex age

# With filtering
tab sex if age > 50

# Complex conditions
tab sex age if region == "Rural" & age > 30
```

### 4. View Results

- Results display in a table format
- Suppressed values (<5) are highlighted in red
- Row counts show filtered dataset size

## API Endpoints

### Upload Dataset
```
POST /api/upload/
Content-Type: multipart/form-data
Body: file=dataset.csv
```

### Get Schema
```
GET /api/schema/?dataset_key=abc123
```

### Execute Query
```
POST /api/query/
Content-Type: application/json
Body: {
  "dataset_key": "abc123",
  "command": "tab sex age if region == 'Rural'"
}
```

## Privacy Protection

### Suppression Rules

1. **Primary Suppression**: Any count < 5 becomes "<5"
2. **Complementary Suppression**: If exactly one cell in a row/column is suppressed, also suppress the second-smallest cell in that row/column
3. **Totals**: Row/column totals recalculated after suppression

### Example

Original table:
```
Sex    Age_Group    Count
M      18-25        3
M      26-35        12
F      18-25        8
F      26-35        2
```

After suppression:
```
Sex    Age_Group    Count
M      18-25        <5
M      26-35        12
F      18-25        8
F      26-35        <5
```

## Development

### Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # Flask-RESTX API routes
│   │   ├── core/         # Core business logic
│   │   └── utils/        # Data loading utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   └── types/        # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/api/routes.py`
2. **Frontend**: Create components in `src/components/`
3. **Types**: Update `src/types/api.ts` for new interfaces

## Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build

1. **Backend:**
   ```bash
   cd backend
   docker build -t pp-query-backend .
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm run build
   docker build -t pp-query-frontend .
   ```

### Environment Variables

- `FLASK_ENV`: Set to `production` for production
- `PYTHONUNBUFFERED`: Set to `1` for Docker logging

## Troubleshooting

### Common Issues

1. **File upload fails**: Check file size (max 1GB) and format (CSV only)
2. **Query syntax error**: Verify Stata-style command format
3. **Memory issues**: Reduce dataset size or increase container memory
4. **CORS errors**: Ensure backend CORS is properly configured

### Logs

- Backend logs: Check Docker container logs or Flask debug output
- Frontend logs: Browser developer console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 