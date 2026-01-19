# Alternative Deployment Methods

The original `requirements.txt` uses strict version pinning which can cause compatibility issues. Here are three alternative deployment methods:

---

## ✅ Method 1: Flexible Requirements (Recommended)

Use the updated requirements file with flexible version ranges:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements-flexible.txt
```

If you still encounter issues, try upgrading pip first:
```powershell
python -m pip install --upgrade pip
pip install -r requirements-flexible.txt
```

---

## 🐳 Method 2: Docker Deployment (Easiest for Production)

### Prerequisites
- Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

### Setup

1. Use the provided Docker configuration files
2. Create a `.env` file in the backend directory with your OpenAI API key
3. Run the following commands:

```powershell
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5001

To stop:
```powershell
docker-compose down
```

---

## 🔄 Method 3: Install Dependencies One by One

If batch installation fails, install packages individually:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install packages one by one
pip install Flask
pip install Flask-CORS
pip install openai
pip install python-dotenv
pip install Pillow
pip install pandas
pip install werkzeug
```

---

## 🌐 Method 4: Use Conda (Alternative to pip)

If pip continues to have issues, try using Conda:

```powershell
# Install Miniconda from: https://docs.conda.io/en/latest/miniconda.html

# Create conda environment
conda create -n budget-app python=3.11
conda activate budget-app

# Install packages
conda install -c conda-forge flask flask-cors python-dotenv pillow pandas
pip install openai  # OpenAI is best installed via pip
```

---

## 🔧 Troubleshooting Common Issues

### Issue: Microsoft Visual C++ errors
**Solution**: Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Issue: Pillow installation fails
**Solution**: 
```powershell
pip install --upgrade Pillow
# Or use pre-built wheels
pip install Pillow --only-binary :all:
```

### Issue: Pandas installation fails
**Solution**:
```powershell
# Install dependencies first
pip install numpy
pip install pandas
```

### Issue: Permission errors
**Solution**: Run PowerShell as Administrator

---

## 📦 Quick Start with Docker (Full Instructions)

### 1. Install Docker Desktop
Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Build and Run
```powershell
# Navigate to project root
cd "c:\Users\mwill\OneDrive\Documents\GitHub\Screenshot-to-Monthly-Budget-app"

# Create .env file if not exists
cd backend
Copy-Item .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Return to project root
cd ..

# Start with Docker
docker-compose up --build
```

### 3. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- Health Check: http://localhost:5001/api/health

---

## 🎯 Recommended Approach

**For Development**: Use Method 1 (Flexible Requirements) or Method 3 (One by One)

**For Production/Sharing**: Use Method 2 (Docker) - ensures consistency across all systems

**If pip is problematic**: Use Method 4 (Conda)
