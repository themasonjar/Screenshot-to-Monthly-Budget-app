# 💰 Budget Management App

A comprehensive full-stack web application for tracking personal finances with AI-powered transaction extraction from bank statements. Upload CSV files or screenshots, categorize transactions, and visualize your spending patterns through interactive dashboards.

## ✨ Features

### 🎯 Core Functionality

- **Project Management**: Create multiple budget projects to organize different financial tracking needs
- **Custom Categories**: Define personalized categories for Income, Expenses, and Savings
- **Dual Data Entry Methods**:
  - Manual entry via editable data tables
  - AI-powered extraction from CSV files and bank statement screenshots
- **Interactive Dashboard**: Comprehensive visualizations including:
  - Monthly income, expenses, and savings breakdown
  - Category distribution pie charts
  - Year-round bar charts with monthly totals
  - Net change calculations
  - Transaction count metrics

### 🤖 AI-Powered Features

- Automatic transaction extraction from bank statement screenshots using GPT-4 Vision
- Intelligent CSV parsing and data normalization
- Smart transaction type detection (Income/Expenses/Savings)
- User verification and editing before final submission

### 📊 Visualizations

- **3 Pie Charts**: Individual breakdown for Income, Expenses, and Savings categories
- **Bar Chart**: Monthly totals with toggle between Income/Expenses/Savings views
- **Month Selector**: Filter all visualizations by selected month
- **Highlighted Current Month**: Visual emphasis on selected month in bar chart

## 🛠️ Tech Stack

### Backend
- **Python 3.x** with **Flask** - REST API framework
- **Upstash Redis** - Persistent datastore (serverless-friendly for Vercel)
- **OpenAI API** - GPT-4 and GPT-4 Vision for AI extraction
- **Pandas** - CSV data processing
- **Pillow** - Image processing

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast development and build tool
- **Chart.js** with **react-chartjs-2** - Professional data visualizations
- **Axios** - HTTP client for API communication
- **CSS3** - Custom responsive styling

## 📁 Project Structure

```
Screenshot-to-Monthly-Budget-app/
├── api/
│   └── index.py               # Vercel Python Serverless Function entrypoint
├── backend/
│   ├── app.py                 # Flask API server
│   ├── database.py            # Database models and operations
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template (local dev)
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── utils/            # API client
│   │   ├── styles/           # CSS styles
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── requirements.txt           # Root Python deps (for Vercel runtime)
├── vercel.json                # Vercel build + routing config
├── README.md
└── SETUP_GUIDE.md
```

## 🚀 Quick Start

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed installation instructions.

### TL;DR

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY + Upstash env vars
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## 📖 Usage Guide

1. **Create a Budget Project** - Start by creating a new project with a descriptive name
2. **Set Up Categories** - Define custom categories for Income, Expenses, and Savings
3. **Add Transactions** - Use manual entry or AI-powered file upload
4. **View Dashboard** - Analyze your finances with interactive charts and metrics
5. **Manage Data** - Edit categories, update transactions, or delete projects

## 🎨 Key Features

### Project & Category Management
- Three-column layout for Income, Expenses, and Savings categories
- Deletable category buttons with X icon
- Dynamic category dropdowns based on transaction type

### Data Entry
- Manual entry with editable data tables
- AI-powered CSV and screenshot processing
- User verification before submission
- Batch transaction import

### Dashboard Visualizations
- Month selector (mm/yyyy format)
- Total transactions metric
- Monthly breakdown (Income, Expenses, Savings)
- 3 pie charts showing category distributions
- Bar chart with 12-month view (Jan-Dec)
- Toggle buttons to switch between Income/Expenses/Savings
- Highlighted selected month in bar chart
- Net gain/loss calculation

### Security
- Environment variable management for API keys
- SQL injection prevention
- CORS configuration
- Input validation

## 📊 API Endpoints

- **Projects**: GET, POST, DELETE
- **Categories**: GET, POST, DELETE
- **Transactions**: GET, POST, PUT, DELETE, BATCH
- **Analytics**: Summary, Breakdown
- **AI**: Extract data from files

See inline API documentation in `backend/app.py`

## 🔐 Environment Variables

### Backend

- **`OPENAI_API_KEY`**: required for AI extraction endpoints
- **`UPSTASH_REDIS_REST_URL`**: required for persistence (Upstash Redis REST URL)
- **`UPSTASH_REDIS_REST_TOKEN`**: required for persistence (Upstash Redis REST token)

## ☁️ Deploy to Vercel (Frontend + API in one project)

This repository is configured to deploy as a single Vercel project:
- The React app is built from `frontend/`
- The Flask API is exposed as a Vercel Python Serverless Function via `api/index.py`
- Requests to **`/api/*`** are routed to Flask; all other routes serve the SPA

### 1) Import the repo into Vercel

Follow Vercel’s import flow to bring in the existing Git repository and deploy it:  
[Import an existing project](https://vercel.com/docs/getting-started-with-vercel/import)

### 2) Add the Upstash Redis integration

Install and connect Upstash Redis to your Vercel project (create a new Upstash account or link an existing one).  
After connecting, Vercel will add the required Redis env vars to the project and **you must redeploy** for them to take effect.  
[Vercel - Upstash Redis Integration](https://upstash.com/docs/redis/howto/vercelintegration)

### 3) Set required environment variables

In Vercel Project Settings → Environment Variables:
- Set **`OPENAI_API_KEY`**
- Confirm Upstash created:
  - **`UPSTASH_REDIS_REST_URL`**
  - **`UPSTASH_REDIS_REST_TOKEN`**

### 4) Verify after deploy

- Open the deployed site
- Check API health at `GET /api/health`

## 🧪 Testing

The application includes comprehensive error handling, input validation, loading states, and user feedback for a robust user experience.

## 🚧 Future Enhancements

- Export to PDF/Excel
- Budget goals and alerts
- Recurring transactions
- Multi-currency support
- Mobile app
- User authentication
- Cloud database
- Advanced search and filtering

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using React, Flask, and AI**
