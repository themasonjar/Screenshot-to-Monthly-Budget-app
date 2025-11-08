import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function DataEntry({ projectId, onComplete }) {
  const [categories, setCategories] = useState({
    Income: [],
    Expenses: [],
    Savings: []
  });
  const [rows, setRows] = useState([
    { date: '', type: '', category: '', amount: '', description: '' }
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadCategories();
  }, [projectId]);

  const loadCategories = async () => {
    try {
      const response = await api.getCategories(projectId);
      const categoriesByType = {
        Income: [],
        Expenses: [],
        Savings: []
      };

      response.data.categories.forEach((cat) => {
        categoriesByType[cat.type].push(cat);
      });

      setCategories(categoriesByType);
      setLoading(false);
    } catch (err) {
      setError('Failed to load categories');
      setLoading(false);
    }
  };

  const handleAddRow = () => {
    setRows([...rows, { date: '', type: '', category: '', amount: '', description: '' }]);
  };

  const handleRemoveRow = (index) => {
    if (rows.length > 1) {
      setRows(rows.filter((_, i) => i !== index));
    }
  };

  const handleRowChange = (index, field, value) => {
    const newRows = [...rows];
    newRows[index][field] = value;

    // Reset category when type changes
    if (field === 'type') {
      newRows[index].category = '';
    }

    setRows(newRows);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate all rows
    const validRows = rows.filter((row) =>
      row.date && row.type && row.category && row.amount
    );

    if (validRows.length === 0) {
      setError('Please fill in at least one complete transaction');
      return;
    }

    try {
      const transactions = validRows.map((row) => ({
        date: row.date,
        type: row.type,
        category: row.category,
        amount: parseFloat(row.amount),
        description: row.description
      }));

      await api.addTransactionsBatch(projectId, transactions);
      setSuccess(`Successfully added ${transactions.length} transaction(s)!`);

      // Reset form
      setRows([{ date: '', type: '', category: '', amount: '', description: '' }]);

      // Navigate back after 1.5 seconds
      setTimeout(() => {
        onComplete();
      }, 1500);
    } catch (err) {
      setError('Failed to save transactions');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="card">
      <h2>Manual Data Entry</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Enter your transactions manually. Add multiple rows before submitting.
      </p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Amount ($)</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  <td>
                    <input
                      type="date"
                      value={row.date}
                      onChange={(e) => handleRowChange(index, 'date', e.target.value)}
                      required
                    />
                  </td>
                  <td>
                    <select
                      value={row.type}
                      onChange={(e) => handleRowChange(index, 'type', e.target.value)}
                      required
                    >
                      <option value="">Select...</option>
                      <option value="Income">Income</option>
                      <option value="Expenses">Expenses</option>
                      <option value="Savings">Savings</option>
                    </select>
                  </td>
                  <td>
                    <select
                      value={row.category}
                      onChange={(e) => handleRowChange(index, 'category', e.target.value)}
                      required
                      disabled={!row.type}
                    >
                      <option value="">Select...</option>
                      {row.type &&
                        categories[row.type].map((cat) => (
                          <option key={cat.id} value={cat.name}>
                            {cat.name}
                          </option>
                        ))}
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={row.amount}
                      onChange={(e) => handleRowChange(index, 'amount', e.target.value)}
                      placeholder="0.00"
                      required
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={row.description}
                      onChange={(e) => handleRowChange(index, 'description', e.target.value)}
                      placeholder="Optional note"
                    />
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-small btn-danger"
                      onClick={() => handleRemoveRow(index)}
                      disabled={rows.length === 1}
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button type="button" className="btn btn-secondary" onClick={handleAddRow}>
            + Add Row
          </button>
          <button type="submit" className="btn btn-success">
            Save All Transactions
          </button>
          <button type="button" className="btn btn-secondary" onClick={onComplete}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default DataEntry;
