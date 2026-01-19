# 🚀 Quick Setup Guide

## Prerequisites

- Node.js v16+ and npm
- Python 3.8+
- OpenAI API Key (for AI features)
- Upstash Redis database (for persistence)

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
# Edit .env and add your OPENAI_API_KEY + Upstash credentials

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

**Upstash env vars missing**: The backend requires Upstash Redis for persistence. Ensure these are set:
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

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
UPSTASH_REDIS_REST_URL=https://your-upstash-rest-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-rest-token
FLASK_ENV=development
FLASK_DEBUG=True
```

## Production Deployment

### Vercel (recommended)

This repo is configured to deploy **frontend + API together** on Vercel.

1. Import the Git repository into Vercel:  
   [Import an existing project](https://vercel.com/docs/getting-started-with-vercel/import)

2. Add the Upstash Redis integration to the Vercel project and connect a Redis database.  
   After env vars are added, **redeploy** for them to take effect:  
   [Vercel - Upstash Redis Integration](https://upstash.com/docs/redis/howto/vercelintegration)

3. In Vercel Project Settings → Environment Variables:
   - Set `OPENAI_API_KEY`
   - Confirm Upstash created `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`

4. Deploy and verify:
   - Visit the deployed site
   - Check API health at `GET /api/health`

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
