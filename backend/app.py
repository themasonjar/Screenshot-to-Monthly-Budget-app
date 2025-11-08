from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import os
from dotenv import load_dotenv
import openai
import base64
from io import BytesIO
from PIL import Image
import pandas as pd
import json
from datetime import datetime
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize database
db = Database()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY', '')


# ==================== PROJECT ENDPOINTS ====================

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = db.get_all_projects()
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'success': False, 'error': 'Project name is required'}), 400

        project_id = db.create_project(name)
        return jsonify({'success': True, 'project_id': project_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404

        return jsonify({'success': True, 'project': project})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        deleted = db.delete_project(project_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Project not found'}), 404

        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CATEGORY ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/categories', methods=['GET'])
def get_categories(project_id):
    """Get categories for a project"""
    try:
        category_type = request.args.get('type')
        categories = db.get_categories(project_id, category_type)
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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

        category_id = db.add_category(project_id, name, category_type)
        return jsonify({'success': True, 'category_id': category_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        deleted = db.delete_category(category_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Category not found'}), 404

        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== TRANSACTION ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/transactions', methods=['GET'])
def get_transactions(project_id):
    """Get transactions for a project"""
    try:
        month = request.args.get('month')
        transactions = db.get_transactions(project_id, month)
        return jsonify({'success': True, 'transactions': transactions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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

        transaction_id = db.add_transaction(
            project_id=project_id,
            date=data['date'],
            trans_type=data['type'],
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description', '')
        )

        return jsonify({'success': True, 'transaction_id': transaction_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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

        transaction_ids = db.add_transactions_batch(transactions)
        return jsonify({'success': True, 'transaction_ids': transaction_ids})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update a transaction"""
    try:
        data = request.json
        updated = db.update_transaction(transaction_id, data)

        if not updated:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

        return jsonify({'success': True, 'message': 'Transaction updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        deleted = db.delete_transaction(transaction_id)
        if not deleted:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404

        return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/summary', methods=['GET'])
def get_summary(project_id):
    """Get monthly summary for a project"""
    try:
        summary = db.get_monthly_summary(project_id)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>/breakdown', methods=['GET'])
def get_breakdown(project_id):
    """Get category breakdown for a specific month"""
    try:
        month = request.args.get('month')
        trans_type = request.args.get('type')

        if not month or not trans_type:
            return jsonify({'success': False, 'error': 'Month and type are required'}), 400

        breakdown = db.get_category_breakdown(project_id, month, trans_type)
        return jsonify({'success': True, 'breakdown': breakdown})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
                csv_content = df.to_string()

                # Use OpenAI to extract structured data from CSV
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a financial data extraction assistant. Extract transaction data from the provided CSV content and return it as a JSON array.
                            Each transaction should have: date (YYYY-MM-DD format), amount (positive number), and description.
                            Determine if each transaction is Income, Expenses, or Savings based on context (negative amounts or debits = Expenses, positive or credits = Income, transfers to savings = Savings).
                            Return ONLY a valid JSON array, no other text."""
                        },
                        {
                            "role": "user",
                            "content": f"Extract transaction data from this CSV:\n\n{csv_content}"
                        }
                    ],
                    temperature=0.3
                )

                result = response.choices[0].message.content.strip()
                # Remove markdown code blocks if present
                result = re.sub(r'^```json\s*', '', result)
                result = re.sub(r'\s*```$', '', result)
                extracted_data = json.loads(result)

            except Exception as e:
                return jsonify({'success': False, 'error': f'CSV processing error: {str(e)}'}), 500

        else:  # Screenshot/Image
            try:
                # Read image and convert to base64
                image = Image.open(file.stream)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                # Use OpenAI Vision to extract data from screenshot
                response = openai.chat.completions.create(
                    model="gpt-4-vision-preview",
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
                return jsonify({'success': False, 'error': f'Image processing error: {str(e)}'}), 500

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
    return jsonify({
        'success': True,
        'message': 'Budget Management API is running',
        'openai_configured': bool(openai.api_key)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
