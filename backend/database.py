import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path='budget_app.db'):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Create a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Income', 'Expenses', 'Savings')),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Income', 'Expenses', 'Savings')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    # Project operations
    def create_project(self, name: str) -> int:
        """Create a new project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO projects (name) VALUES (?)', (name,))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return projects

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get a specific project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all associated data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # Category operations
    def add_category(self, project_id: int, name: str, category_type: str) -> int:
        """Add a category to a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO categories (project_id, name, type) VALUES (?, ?, ?)',
            (project_id, name, category_type)
        )
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id

    def get_categories(self, project_id: int, category_type: Optional[str] = None) -> List[Dict]:
        """Get categories for a project"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if category_type:
            cursor.execute(
                'SELECT * FROM categories WHERE project_id = ? AND type = ?',
                (project_id, category_type)
            )
        else:
            cursor.execute('SELECT * FROM categories WHERE project_id = ?', (project_id,))

        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories

    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # Transaction operations
    def add_transaction(self, project_id: int, date: str, trans_type: str,
                       category: str, amount: float, description: str = '') -> int:
        """Add a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO transactions (project_id, date, type, category, amount, description)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (project_id, date, trans_type, category, amount, description)
        )
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id

    def add_transactions_batch(self, transactions: List[Dict]) -> List[int]:
        """Add multiple transactions at once"""
        conn = self.get_connection()
        cursor = conn.cursor()
        transaction_ids = []

        for trans in transactions:
            cursor.execute(
                '''INSERT INTO transactions (project_id, date, type, category, amount, description)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (trans['project_id'], trans['date'], trans['type'],
                 trans['category'], trans['amount'], trans.get('description', ''))
            )
            transaction_ids.append(cursor.lastrowid)

        conn.commit()
        conn.close()
        return transaction_ids

    def get_transactions(self, project_id: int, month: Optional[str] = None) -> List[Dict]:
        """Get transactions for a project, optionally filtered by month"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if month:
            # month format: "mm/yyyy"
            cursor.execute(
                '''SELECT * FROM transactions
                   WHERE project_id = ? AND strftime('%m/%Y', date) = ?
                   ORDER BY date DESC''',
                (project_id, month)
            )
        else:
            cursor.execute(
                'SELECT * FROM transactions WHERE project_id = ? ORDER BY date DESC',
                (project_id,)
            )

        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions

    def update_transaction(self, transaction_id: int, data: Dict) -> bool:
        """Update a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []

        for key in ['date', 'type', 'category', 'amount', 'description']:
            if key in data:
                fields.append(f'{key} = ?')
                values.append(data[key])

        if not fields:
            return False

        values.append(transaction_id)
        query = f'UPDATE transactions SET {", ".join(fields)} WHERE id = ?'

        cursor.execute(query, values)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def get_monthly_summary(self, project_id: int) -> Dict:
        """Get summary of all transactions grouped by month and type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%m', date) as month,
                strftime('%Y', date) as year,
                type,
                SUM(amount) as total
            FROM transactions
            WHERE project_id = ?
            GROUP BY strftime('%Y-%m', date), type
            ORDER BY year, month
        ''', (project_id,))

        results = cursor.fetchall()
        conn.close()

        # Organize by month and type
        summary = {}
        for row in results:
            month_key = f"{row['month']}/{row['year']}"
            if month_key not in summary:
                summary[month_key] = {'Income': 0, 'Expenses': 0, 'Savings': 0}
            summary[month_key][row['type']] = row['total']

        return summary

    def get_category_breakdown(self, project_id: int, month: str, trans_type: str) -> Dict:
        """Get category breakdown for a specific month and type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE project_id = ? AND strftime('%m/%Y', date) = ? AND type = ?
            GROUP BY category
        ''', (project_id, month, trans_type))

        results = cursor.fetchall()
        conn.close()

        return {row['category']: row['total'] for row in results}
