# 🚀 Quick Setup Guide

## Prerequisites

- Node.js v16+ and npm
- Python 3.8+
- OpenAI API Key (for AI features)

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start server
python app.py
```

Backend runs on: `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

## Quick Start

1. Open `http://localhost:3000` in your browser
2. Create a new budget project
3. Set up your income, expense, and savings categories
4. Start adding transactions via manual entry or file upload
5. View your financial dashboard with interactive charts

## Troubleshooting

### Backend Issues

**Database not created**: The SQLite database is auto-created on first run.

**OpenAI API errors**: Make sure your API key is valid and has credits.

**Port 5000 already in use**: Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Frontend Issues

**Port 3000 already in use**: Vite will automatically suggest an alternative port.

**API connection errors**: Ensure backend is running on port 5000.

**Dependencies not installing**: Try deleting `node_modules` and `package-lock.json`, then run `npm install` again.

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=sk-your-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

## Production Deployment

### Backend

1. Set `FLASK_DEBUG=False` in `.env`
2. Use a production WSGI server (gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Frontend

1. Build the production bundle:
   ```bash
   npm run build
   ```

2. Serve the `dist` folder using a static file server or CDN

## API Health Check

Test if backend is running:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "Budget Management API is running",
  "openai_configured": true
}
```

## Demo Data

To test the application, create a project with these sample categories:

**Income**: Salary, Freelance, Investments
**Expenses**: Rent, Groceries, Transportation, Utilities
**Savings**: Emergency Fund, Vacation, Retirement

Then add some sample transactions to see the charts populate.

## Support

For issues, check the main README.md or open a GitHub issue.
