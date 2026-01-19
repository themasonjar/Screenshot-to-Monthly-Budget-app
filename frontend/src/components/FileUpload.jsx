import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function FileUpload({ projectId, onComplete }) {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('');
  const [extractedData, setExtractedData] = useState([]);
  const [categories, setCategories] = useState({
    Income: [],
    Expenses: [],
    Savings: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState(1); // 1: upload, 2: verify/edit

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
    } catch (err) {
      setError('Failed to load categories');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);

      // Determine file type
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFileType('csv');
      } else if (selectedFile.type === 'application/json' || selectedFile.name.endsWith('.json')) {
        setFileType('json');
      } else if (
        selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        selectedFile.name.endsWith('.xlsx')
      ) {
        setFileType('excel');
      } else if (selectedFile.type.startsWith('image/')) {
        setFileType('image');
      } else {
        setError('Unsupported file type. Please upload CSV, JSON, Excel, or Image (PNG, JPG).');
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError('');

    try {
      const response = await api.extractData(file, fileType);
      const data = response.data.data;

      // Initialize extracted data with empty categories
      const processedData = data.map((item) => ({
        ...item,
        category: '' // User must assign category
      }));

      setExtractedData(processedData);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to extract data from file');
    } finally {
      setLoading(false);
    }
  };

  const handleDataChange = (index, field, value) => {
    const newData = [...extractedData];
    newData[index][field] = value;

    // Reset category when type changes
    if (field === 'type') {
      newData[index].category = '';
    }

    setExtractedData(newData);
  };

  const handleRemoveRow = (index) => {
    setExtractedData(extractedData.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    setError('');
    setSuccess('');

    // Validate all rows have categories
    const invalidRows = extractedData.filter((row) => !row.category);
    if (invalidRows.length > 0) {
      setError('Please assign categories to all transactions');
      return;
    }

    try {
      const transactions = extractedData.map((row) => ({
        date: row.date,
        type: row.type,
        category: row.category,
        amount: parseFloat(row.amount),
        description: row.description || ''
      }));

      await api.addTransactionsBatch(projectId, transactions);
      setSuccess(`Successfully imported ${transactions.length} transaction(s)!`);

      // Navigate back after 1.5 seconds
      setTimeout(() => {
        onComplete();
      }, 1500);
    } catch (err) {
      setError('Failed to save transactions');
    }
  };

  if (step === 1) {
    return (
      <div className="card">
        <h2>Upload Bank Statement</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Upload a CSV file or screenshot of your bank statement. AI will extract the transaction data for you.
        </p>

        {error && (
          <div className="error" style={{ whiteSpace: 'pre-wrap', textAlign: 'left', padding: '15px', border: '1px solid #f5c6cb', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '20px' }}>
            {error}
          </div>
        )}

        <div className="file-upload" onClick={() => document.getElementById('file-input').click()}>
          <input
            id="file-input"
            type="file"
            accept=".csv,.json,.xlsx,.png,.jpg,.jpeg,image/*"
            onChange={handleFileSelect}
          />
          <div>
            <p style={{ fontSize: '3rem', marginBottom: '10px' }}>📁</p>
            <p style={{ fontSize: '1.2rem', fontWeight: '500' }}>
              {file ? file.name : 'Click to select file'}
            </p>
            <p style={{ color: '#666', marginTop: '10px' }}>
              Supports: CSV, JSON, Excel, PNG, JPG
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? 'Processing...' : 'Extract Data'}
          </button>
          <button className="btn btn-secondary" onClick={onComplete}>
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Verify & Assign Categories</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Review the extracted data and assign categories to each transaction before saving.
      </p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

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
            {extractedData.map((row, index) => (
              <tr key={index}>
                <td>
                  <input
                    type="date"
                    value={row.date}
                    onChange={(e) => handleDataChange(index, 'date', e.target.value)}
                  />
                </td>
                <td>
                  <select
                    value={row.type}
                    onChange={(e) => handleDataChange(index, 'type', e.target.value)}
                  >
                    <option value="Income">Income</option>
                    <option value="Expenses">Expenses</option>
                    <option value="Savings">Savings</option>
                  </select>
                </td>
                <td>
                  <select
                    value={row.category}
                    onChange={(e) => handleDataChange(index, 'category', e.target.value)}
                    style={{ borderColor: !row.category ? '#dc3545' : '#e0e0e0' }}
                  >
                    <option value="">Select category...</option>
                    {categories[row.type].map((cat) => (
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
                    value={row.amount}
                    onChange={(e) => handleDataChange(index, 'amount', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={row.description || ''}
                    onChange={(e) => handleDataChange(index, 'description', e.target.value)}
                  />
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-small btn-danger"
                    onClick={() => handleRemoveRow(index)}
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
        <button className="btn btn-success" onClick={handleSubmit}>
          Save {extractedData.length} Transaction(s)
        </button>
        <button className="btn btn-secondary" onClick={() => setStep(1)}>
          Back to Upload
        </button>
        <button className="btn btn-secondary" onClick={onComplete}>
          Cancel
        </button>
      </div>
    </div>
  );
}

export default FileUpload;
