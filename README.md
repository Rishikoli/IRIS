# IRIS RegTech Platform

Intelligent Risk & Investigation System for detecting, explaining, and forecasting fraud chains affecting retail investors in India.

## Project Structure

```
iris-regtech-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── database.py     # Database configuration
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── crud.py         # Database operations
│   │   └── routers/        # API endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Development server
│   └── .env.example       # Environment variables template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── App.tsx        # Main app component
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── README.md              # This file
```

## Features

- **Tip Risk Analysis**: AI-powered analysis of investment tips for fraud detection
- **Advisor Verification**: SEBI registration verification for financial advisors
- **Document Authentication**: PDF authenticity checking with OCR and AI analysis
- **Regulatory Dashboard**: Real-time fraud monitoring and visualization
- **Risk Forecasting**: AI-powered predictions of fraud hotspots
- **Human-in-the-Loop Review**: Manual review and override of AI decisions

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (for demo - PostgreSQL recommended for production)
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library with TypeScript
- **Vite**: Build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Lucide React**: Icon library

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the development server:
   ```bash
   python run.py
   ```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database

The application uses SQLite for development with the following core entities:
- **Tips**: Investment tips submitted for analysis
- **Assessments**: AI risk assessments of tips
- **PDF Checks**: Document authenticity verification results

The database file (`iris_regtech.db`) will be created automatically when you first run the backend.

## Development Status

This is the initial project setup with core infrastructure. The following features are implemented:

✅ **Completed:**
- FastAPI backend with CORS middleware
- React frontend with TypeScript and Tailwind CSS
- SQLite database with SQLAlchemy models
- Basic CRUD operations for core entities
- Responsive navigation and routing
- API service layer

🚧 **In Progress:**
- Individual feature implementations (tip analysis, advisor verification, etc.)

## Contributing

This is a demonstration project for the IRIS RegTech platform. Future tasks will implement the specific features outlined in the requirements.

## License

This project is for demonstration purposes only.