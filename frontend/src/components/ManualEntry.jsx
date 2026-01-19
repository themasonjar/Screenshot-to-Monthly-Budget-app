import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function ManualEntry({ projectId, onComplete }) {
    const [categories, setCategories] = useState({
        Income: [],
        Expenses: [],
        Savings: []
    });
    const [transactions, setTransactions] = useState([]);
    const [availableMonths, setAvailableMonths] = useState([]);
    const [selectedMonth, setSelectedMonth] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({});
    const [newRow, setNewRow] = useState({
        date: new Date().toISOString().split('T')[0],
        type: 'Income',
        category: '',
        amount: '',
        description: ''
    });

    useEffect(() => {
        loadInitialData();
    }, [projectId]);

    useEffect(() => {
        if (selectedMonth) {
            loadTransactions();
        }
    }, [selectedMonth]);

    const loadInitialData = async () => {
        try {
            setLoading(true);
            const [categoriesRes, summaryRes] = await Promise.all([
                api.getCategories(projectId),
                api.getSummary(projectId)
            ]);

            // Process categories
            const categoriesByType = {
                Income: [],
                Expenses: [],
                Savings: []
            };
            categoriesRes.data.categories.forEach((cat) => {
                categoriesByType[cat.type].push(cat);
            });
            setCategories(categoriesByType);

            // Process months
            const months = Object.keys(summaryRes.data.summary).sort().reverse();
            setAvailableMonths(months);

            // Select current month or first available
            if (months.length > 0) {
                const currentDate = new Date();
                const currentMonthStr = `${String(currentDate.getMonth() + 1).padStart(2, '0')}/${currentDate.getFullYear()}`;
                setSelectedMonth(months.includes(currentMonthStr) ? currentMonthStr : months[0]);
            } else {
                // Default to current month if no data
                const currentDate = new Date();
                setSelectedMonth(`${String(currentDate.getMonth() + 1).padStart(2, '0')}/${currentDate.getFullYear()}`);
                setLoading(false);
            }
        } catch (err) {
            setError('Failed to load initial data');
            setLoading(false);
        }
    };

    const loadTransactions = async () => {
        try {
            setLoading(true);
            const response = await api.getTransactions(projectId, selectedMonth);
            setTransactions(response.data.transactions);
            setLoading(false);
        } catch (err) {
            setError('Failed to load transactions');
            setLoading(false);
        }
    };

    const handleEdit = (transaction) => {
        setEditingId(transaction.id);
        setEditForm({ ...transaction });
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditForm({});
    };

    const handleEditChange = (field, value) => {
        setEditForm(prev => ({ ...prev, [field]: value }));
    };

    const handleSaveEdit = async () => {
        try {
            await api.updateTransaction(editingId, {
                ...editForm,
                amount: parseFloat(editForm.amount)
            });
            setSuccess('Transaction updated successfully');
            setEditingId(null);
            loadTransactions();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to update transaction');
            setTimeout(() => setError(''), 3000);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this transaction?')) {
            try {
                await api.deleteTransaction(id);
                setSuccess('Transaction deleted successfully');
                loadTransactions();
                setTimeout(() => setSuccess(''), 3000);
            } catch (err) {
                setError('Failed to delete transaction');
                setTimeout(() => setError(''), 3000);
            }
        }
    };

    const handleNewRowChange = (field, value) => {
        setNewRow(prev => {
            const updated = { ...prev, [field]: value };
            if (field === 'type') updated.category = ''; // Reset category on type change
            return updated;
        });
    };

    const handleAddRow = async () => {
        if (!newRow.date || !newRow.category || !newRow.amount) {
            setError('Please fill in all required fields');
            setTimeout(() => setError(''), 3000);
            return;
        }

        try {
            await api.addTransaction(projectId, {
                ...newRow,
                amount: parseFloat(newRow.amount)
            });
            setSuccess('Transaction added successfully');
            setNewRow({
                date: new Date().toISOString().split('T')[0],
                type: 'Income',
                category: '',
                amount: '',
                description: ''
            });
            loadTransactions();
            // Refresh months list in case a new month was added
            const summaryRes = await api.getSummary(projectId);
            const months = Object.keys(summaryRes.data.summary).sort().reverse();
            setAvailableMonths(months);

            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to add transaction');
            setTimeout(() => setError(''), 3000);
        }
    };

    if (loading && !transactions.length && !availableMonths.length) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2>Manage Data</h2>
                <button className="btn btn-secondary" onClick={onComplete}>
                    ← Back to Dashboard
                </button>
            </div>

            <div className="input-group" style={{ marginBottom: '20px' }}>
                <label>Select Month</label>
                <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                    style={{ maxWidth: '300px' }}
                >
                    {availableMonths.map((month) => (
                        <option key={month} value={month}>
                            {month}
                        </option>
                    ))}
                </select>
            </div>

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
                        {/* New Row Input */}
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                            <td>
                                <input
                                    type="date"
                                    value={newRow.date}
                                    onChange={(e) => handleNewRowChange('date', e.target.value)}
                                />
                            </td>
                            <td>
                                <select
                                    value={newRow.type}
                                    onChange={(e) => handleNewRowChange('type', e.target.value)}
                                >
                                    <option value="Income">Income</option>
                                    <option value="Expenses">Expenses</option>
                                    <option value="Savings">Savings</option>
                                </select>
                            </td>
                            <td>
                                <select
                                    value={newRow.category}
                                    onChange={(e) => handleNewRowChange('category', e.target.value)}
                                    disabled={!newRow.type}
                                >
                                    <option value="">Select...</option>
                                    {categories[newRow.type]?.map((cat) => (
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
                                    value={newRow.amount}
                                    onChange={(e) => handleNewRowChange('amount', e.target.value)}
                                    placeholder="0.00"
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={newRow.description}
                                    onChange={(e) => handleNewRowChange('description', e.target.value)}
                                    placeholder="New transaction..."
                                />
                            </td>
                            <td>
                                <button className="btn btn-success" onClick={handleAddRow}>
                                    + Add
                                </button>
                            </td>
                        </tr>

                        {/* Existing Transactions */}
                        {transactions.map((t) => (
                            <tr key={t.id}>
                                {editingId === t.id ? (
                                    <>
                                        <td>
                                            <input
                                                type="date"
                                                value={editForm.date}
                                                onChange={(e) => handleEditChange('date', e.target.value)}
                                            />
                                        </td>
                                        <td>
                                            <select
                                                value={editForm.type}
                                                onChange={(e) => handleEditChange('type', e.target.value)}
                                            >
                                                <option value="Income">Income</option>
                                                <option value="Expenses">Expenses</option>
                                                <option value="Savings">Savings</option>
                                            </select>
                                        </td>
                                        <td>
                                            <select
                                                value={editForm.category}
                                                onChange={(e) => handleEditChange('category', e.target.value)}
                                            >
                                                <option value="">Select...</option>
                                                {categories[editForm.type]?.map((cat) => (
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
                                                value={editForm.amount}
                                                onChange={(e) => handleEditChange('amount', e.target.value)}
                                            />
                                        </td>
                                        <td>
                                            <input
                                                type="text"
                                                value={editForm.description || ''}
                                                onChange={(e) => handleEditChange('description', e.target.value)}
                                            />
                                        </td>
                                        <td>
                                            <button className="btn btn-success btn-small" onClick={handleSaveEdit} style={{ marginRight: '5px' }}>
                                                Save
                                            </button>
                                            <button className="btn btn-secondary btn-small" onClick={handleCancelEdit}>
                                                Cancel
                                            </button>
                                        </td>
                                    </>
                                ) : (
                                    <>
                                        <td>{new Date(t.date).toLocaleDateString()}</td>
                                        <td>
                                            <span className={`badge badge-${t.type.toLowerCase()}`}>
                                                {t.type}
                                            </span>
                                        </td>
                                        <td>{t.category}</td>
                                        <td>${t.amount.toFixed(2)}</td>
                                        <td>{t.description}</td>
                                        <td>
                                            <button
                                                className="btn btn-secondary btn-small"
                                                onClick={() => handleEdit(t)}
                                                style={{ marginRight: '5px' }}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                className="btn btn-danger btn-small"
                                                onClick={() => handleDelete(t.id)}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </>
                                )}
                            </tr>
                        ))}

                        {transactions.length === 0 && (
                            <tr>
                                <td colSpan="6" style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
                                    No transactions found for {selectedMonth}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ManualEntry;
