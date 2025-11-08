import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function ProjectSetup({ projectId, onComplete }) {
  const [categories, setCategories] = useState({
    Income: [],
    Expenses: [],
    Savings: []
  });
  const [newCategory, setNewCategory] = useState({
    Income: '',
    Expenses: '',
    Savings: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  const handleAddCategory = async (type) => {
    const name = newCategory[type].trim();
    if (!name) return;

    try {
      await api.addCategory(projectId, name, type);
      setNewCategory({ ...newCategory, [type]: '' });
      loadCategories();
    } catch (err) {
      setError('Failed to add category');
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    try {
      await api.deleteCategory(categoryId);
      loadCategories();
    } catch (err) {
      setError('Failed to delete category');
    }
  };

  const canProceed = () => {
    return categories.Income.length > 0 ||
           categories.Expenses.length > 0 ||
           categories.Savings.length > 0;
  };

  if (loading) {
    return <div className="loading">Loading categories...</div>;
  }

  return (
    <div className="card">
      <h2>Setup Budget Categories</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Define categories for tracking your income, expenses, and savings.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="category-grid">
        {['Income', 'Expenses', 'Savings'].map((type) => (
          <div key={type} className="category-column">
            <h3>{type}</h3>

            <div className="category-list">
              {categories[type].map((cat) => (
                <div key={cat.id} className={`category-item ${type.toLowerCase()}`}>
                  <span>{cat.name}</span>
                  <button
                    onClick={() => handleDeleteCategory(cat.id)}
                    title="Delete category"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>

            <div className="add-category">
              <input
                type="text"
                value={newCategory[type]}
                onChange={(e) =>
                  setNewCategory({ ...newCategory, [type]: e.target.value })
                }
                placeholder={`Add ${type.toLowerCase()} category`}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddCategory(type);
                  }
                }}
              />
              <button
                className="btn btn-small btn-primary"
                onClick={() => handleAddCategory(type)}
              >
                +
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <button
          className="btn btn-primary"
          onClick={onComplete}
          disabled={!canProceed()}
        >
          Continue to Dashboard
        </button>
      </div>
    </div>
  );
}

export default ProjectSetup;
