from flask import Flask, request, jsonify, g
from flask_cors import CORS
try:
    # When imported as a package (e.g. from Vercel `api/index.py`)
    from .database import Database
except ImportError:
    # When run directly for local dev (e.g. `python backend/app.py`)
    from database import Database
import logging
import os
import time
import uuid
from typing import Optional
from dotenv import load_dotenv
import openai
import base64
from io import BytesIO
from PIL import Image
import pandas as pd
import json
from datetime import datetime
import re
from werkzeug.exceptions import HTTPException

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

logger = logging.getLogger("budgetapp")
if not logging.getLogger().handlers:
    # Ensure logs are emitted in serverless environments
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# Lazy DB init so Vercel cold-start import never crashes
_db_instance = None
_db_init_error: Optional[Exception] = None


def get_db() -> Database:
    global _db_instance, _db_init_error
    if _db_instance is not None:
        return _db_instance
    if _db_init_error is not None:
        raise _db_init_error
    try:
        _db_instance = Database()
        return _db_instance
    except Exception as e:
        _db_init_error = e
        raise

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY', '')


@app.before_request
def _assign_request_id_and_log_start():
    g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    g.request_start_time = time.time()
    logger.info(
        json.dumps(
            {
                "event": "request_start",
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
            }
        )
    )


@app.after_request
def _add_request_id_and_log_end(response):
    request_id = getattr(g, "request_id", None)
    if request_id:
        response.headers["X-Request-ID"] = request_id
    start = getattr(g, "request_start_time", None)
    duration_ms = int((time.time() - start) * 1000) if isinstance(start, (int, float)) else None
    logger.info(
        json.dumps(
            {
                "event": "request_end",
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    return response


@app.errorhandler(HTTPException)
def _handle_http_exception(e: HTTPException):
    request_id = getattr(g, "request_id", None)
    logger.warning(
        json.dumps(
            {
                "event": "http_exception",
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": e.code,
                "error": e.description,
            }
        )
    )
    return jsonify({"success": False, "error": e.description, "request_id": request_id}), (e.code or 500)


@app.errorhandler(Exception)
def _handle_unhandled_exception(e: Exception):
    request_id = getattr(g, "request_id", None)
    # Full stack trace to Vercel logs
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "method": getattr(request, "method", None),
            "path": getattr(request, "path", None),
        },
    )
    # Minimal response body; correlate via request_id and logs
    return (
        jsonify({"success": False, "error": "Internal server error", "request_id": request_id}),
        500,
    )


# ==================== PROJECT ENDPOINTS ====================

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = get_db().get_all_projects()
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        logger.exception("get_projects_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'success': False, 'error': 'Project name is required'}), 400

        project_id = get_db().create_project(name)
        return jsonify({'success': True, 'project_id': project_id})
    except Exception as e:
        logger.exception("create_project_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    try:
        project = get_db().get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404

        return jsonify({'success': True, 'project': project})
    except Exception as e:
        logger.exception("get_project_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        deleted = get_db().delete_project(project_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Project not found'}), 404

        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        logger.exception("delete_project_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


# ==================== CATEGORY ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/categories', methods=['GET'])
def get_categories(project_id):
    """Get categories for a project"""
    try:
        category_type = request.args.get('type')
        categories = get_db().get_categories(project_id, category_type)
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        logger.exception("get_categories_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>/categories', methods=['POST'])
def add_category(project_id):
    """Add a category to a project"""
    try:
        data = request.json
        name = data.get('name')
        category_type = data.get('type')

        if not name or not category_type:
            return jsonify({'success': False, 'error': 'Name and type are required'}), 400

        if category_type not in ['Income', 'Expenses', 'Savings']:
            return jsonify({'success': False, 'error': 'Invalid category type'}), 400

        category_id = get_db().add_category(project_id, name, category_type)
        return jsonify({'success': True, 'category_id': category_id})
    except Exception as e:
        logger.exception("add_category_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        deleted = get_db().delete_category(category_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Category not found'}), 404

        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    except Exception as e:
        logger.exception("delete_category_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


# ==================== TRANSACTION ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/transactions', methods=['GET'])
def get_transactions(project_id):
    """Get transactions for a project"""
    try:
        month = request.args.get('month')
        transactions = get_db().get_transactions(project_id, month)
        return jsonify({'success': True, 'transactions': transactions})
    except Exception as e:
        logger.exception("get_transactions_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>/transactions', methods=['POST'])
def add_transaction(project_id):
    """Add a transaction"""
    try:
        data = request.json

        # Validate required fields
        required_fields = ['date', 'type', 'category', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        transaction_id = get_db().add_transaction(
            project_id=project_id,
            date=data['date'],
            trans_type=data['type'],
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description', '')
        )

        return jsonify({'success': True, 'transaction_id': transaction_id})
    except Exception as e:
        logger.exception("add_transaction_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>/transactions/batch', methods=['POST'])
def add_transactions_batch(project_id):
    """Add multiple transactions at once"""
    try:
        data = request.json
        transactions = data.get('transactions', [])

        if not transactions:
            return jsonify({'success': False, 'error': 'No transactions provided'}), 400

        # Add project_id to each transaction
        for trans in transactions:
            trans['project_id'] = project_id

        transaction_ids = get_db().add_transactions_batch(transactions)
        return jsonify({'success': True, 'transaction_ids': transaction_ids})
    except Exception as e:
        logger.exception("add_transactions_batch_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update a transaction"""
    try:
        data = request.json
        updated = get_db().update_transaction(transaction_id, data)

        if not updated:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

        return jsonify({'success': True, 'message': 'Transaction updated successfully'})
    except Exception as e:
        logger.exception("update_transaction_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        deleted = get_db().delete_transaction(transaction_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

        return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
    except Exception as e:
        logger.exception("delete_transaction_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/summary', methods=['GET'])
def get_summary(project_id):
    """Get monthly summary for a project"""
    try:
        summary = get_db().get_monthly_summary(project_id)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        logger.exception("get_summary_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


@app.route('/api/projects/<int:project_id>/breakdown', methods=['GET'])
def get_breakdown(project_id):
    """Get category breakdown for a specific month"""
    try:
        month = request.args.get('month')
        trans_type = request.args.get('type')

        if not month or not trans_type:
            return jsonify({'success': False, 'error': 'Month and type are required'}), 400

        breakdown = get_db().get_category_breakdown(project_id, month, trans_type)
        return jsonify({'success': True, 'breakdown': breakdown})
    except Exception as e:
        logger.exception("get_breakdown_failed")
        return jsonify({'success': False, 'error': str(e), 'request_id': getattr(g, "request_id", None)}), 500


# ==================== AI FILE PROCESSING ENDPOINT ====================

def parse_date(date_str):
    """Parse various date formats and return YYYY-MM-DD"""
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%b %d, %Y',
        '%B %d, %Y',
        '%d %b %Y',
        '%d %B %Y'
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    # If no format matches, return as is
    return date_str


def handle_openai_error(e):
    """Handle OpenAI API errors and return user-friendly messages"""
    error_msg = str(e)
    status_code = 500
    
    # Check for specific error types based on exception class name or message content
    # Note: We use string matching to avoid importing all exception classes if not strictly necessary,
    # but importing them is better practice. For now, we'll check the error object attributes.
    
    if hasattr(e, 'status_code'):
        status_code = e.status_code
    elif hasattr(e, 'http_status'):
        status_code = e.http_status
        
    if status_code == 401:
        return "Authentication Error (401): Your OpenAI API key is invalid or missing. Please check your .env file.", 401
    elif status_code == 429:
        return "Rate Limit/Quota Error (429): You have exceeded your OpenAI API quota or rate limit. Please check your billing details at platform.openai.com/account/billing.", 429
    elif status_code == 404:
        if 'model' in error_msg.lower():
            return "Model Not Found (404): The selected AI model is not available for your API key. You may need to add payment details to your OpenAI account to access GPT-4o.", 404
        return f"Not Found Error (404): {error_msg}", 404
    elif status_code == 500:
        return "OpenAI Server Error (500): OpenAI's servers are currently experiencing issues. Please try again later.", 500
    elif status_code == 503:
        return "Service Unavailable (503): OpenAI's servers are overloaded. Please try again later.", 503
        
    # Generic fallback
    return f"OpenAI API Error: {error_msg}", status_code


def process_chunk_with_ai(content_chunk, content_type="csv"):
    """
    Process a chunk of text content (CSV/Excel) using OpenAI.
    content_type: 'csv' or 'excel'
    """
    system_prompt = """You are a financial data extraction assistant. Extract transaction data from the provided content and return it as a JSON array.
    Each transaction should have: date (YYYY-MM-DD format), amount (positive number), and description.
    Determine if each transaction is Income, Expenses, or Savings based on context (negative amounts or debits = Expenses, positive or credits = Income, transfers to savings = Savings).
    Return ONLY a valid JSON array, no other text."""

    user_prompt = f"Extract transaction data from this {content_type.upper()} chunk:\n\n{content_chunk}"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        result = re.sub(r'^```json\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        return json.loads(result)
    except Exception as e:
        raise e  # Re-raise to be handled by caller


@app.route('/api/extract-data', methods=['POST'])
def extract_data():
    """Extract transaction data from uploaded file using AI"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        file_type = request.form.get('fileType', '')

        if not openai.api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY in .env file'
            }), 500

        extracted_data = []

        if file_type == 'csv':
            # Process CSV file
            try:
                df = pd.read_csv(file)
                extracted_data = []
                
                # Chunking parameters
                chunk_size = 50
                total_rows = len(df)
                
                print(f"Processing CSV with {total_rows} rows in chunks of {chunk_size}...")

                for i in range(0, total_rows, chunk_size):
                    chunk = df.iloc[i:i+chunk_size]
                    csv_content = chunk.to_string()
                    
                    try:
                        chunk_data = process_chunk_with_ai(csv_content, "csv")
                        extracted_data.extend(chunk_data)
                        print(f"  Processed chunk {i//chunk_size + 1}/{(total_rows + chunk_size - 1)//chunk_size}")
                    except Exception as e:
                        print(f"  Error processing chunk starting at row {i}: {e}")
                        # Continue to next chunk or fail? Let's continue but log.
                        # For now, we will fail if AI fails to parse JSON completely, 
                        # but in production partial success might be better.
                        # Re-raising for now to bubble up the OpenAI specific errors.
                        raise e

            except Exception as e:
                if "openai" in str(type(e)).lower():
                    msg, code = handle_openai_error(e)
                    return jsonify({'success': False, 'error': msg}), code
                return jsonify({'success': False, 'error': f'CSV processing error: {str(e)}'}), 500

        elif file_type == 'json':
            # Process JSON file
            try:
                content = json.load(file)
                # Ensure it's a list of transactions
                if isinstance(content, list):
                    extracted_data = content
                elif isinstance(content, dict) and 'transactions' in content:
                    extracted_data = content['transactions']
                else:
                    return jsonify({'success': False, 'error': 'Invalid JSON format. Expected a list of transactions or an object with a "transactions" key.'}), 400
            except Exception as e:
                return jsonify({'success': False, 'error': f'JSON processing error: {str(e)}'}), 500

        elif file_type == 'excel':
            # Process Excel file
            try:
                df = pd.read_excel(file)
                extracted_data = []
                
                # Chunking parameters
                chunk_size = 50
                total_rows = len(df)
                
                print(f"Processing Excel with {total_rows} rows in chunks of {chunk_size}...")

                for i in range(0, total_rows, chunk_size):
                    chunk = df.iloc[i:i+chunk_size]
                    excel_content = chunk.to_string()
                    
                    try:
                        chunk_data = process_chunk_with_ai(excel_content, "excel")
                        extracted_data.extend(chunk_data)
                        print(f"  Processed chunk {i//chunk_size + 1}/{(total_rows + chunk_size - 1)//chunk_size}")
                    except Exception as e:
                        print(f"  Error processing chunk starting at row {i}: {e}")
                        raise e

            except Exception as e:
                if "openai" in str(type(e)).lower():
                    msg, code = handle_openai_error(e)
                    return jsonify({'success': False, 'error': msg}), code
                return jsonify({'success': False, 'error': f'Excel processing error: {str(e)}'}), 500

        elif file_type == 'image':  # Screenshot/Image (PNG, JPG, JPEG)
            try:
                # Read image and convert to base64
                image = Image.open(file.stream)
                buffered = BytesIO()
                # Convert to RGB if necessary (e.g. for JPEGs)
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                image.save(buffered, format="PNG") # Save as PNG for API consistency
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                # Use OpenAI Vision to extract data from screenshot
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Extract all transaction data from this bank statement screenshot. Return a JSON array of transactions.
                                    Each transaction should have: date (YYYY-MM-DD format), amount (positive number), and description.
                                    Determine if each transaction is Income, Expenses, or Savings based on context.
                                    Return ONLY a valid JSON array, no other text."""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )

                result = response.choices[0].message.content.strip()
                # Remove markdown code blocks if present
                result = re.sub(r'^```json\s*', '', result)
                result = re.sub(r'\s*```$', '', result)
                extracted_data = json.loads(result)

            except Exception as e:
                if "openai" in str(type(e)).lower():
                    msg, code = handle_openai_error(e)
                    return jsonify({'success': False, 'error': msg}), code
                return jsonify({'success': False, 'error': f'Image processing error: {str(e)}'}), 500
        
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

        # Normalize dates
        for transaction in extracted_data:
            if 'date' in transaction:
                transaction['date'] = parse_date(transaction['date'])

        return jsonify({'success': True, 'data': extracted_data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    redis_configured = bool(os.getenv("UPSTASH_REDIS_REST_URL")) and bool(os.getenv("UPSTASH_REDIS_REST_TOKEN"))
    redis_ok = False
    redis_error = None
    if redis_configured:
        try:
            db = get_db()
            # Upstash REST client supports ping()
            db.redis.ping()
            redis_ok = True
        except Exception as e:
            redis_error = str(e)

    return jsonify(
        {
            'success': True,
            'message': 'Budget Management API is running',
            'openai_configured': bool(openai.api_key),
            'redis_configured': redis_configured,
            'redis_ok': redis_ok,
            'redis_error': redis_error,
            'request_id': getattr(g, "request_id", None),
        }
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
