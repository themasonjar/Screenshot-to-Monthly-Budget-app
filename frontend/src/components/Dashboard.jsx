import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import api from '../utils/api';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function Dashboard({ projectId, projectName, onNavigate, onBack }) {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState({});
  const [selectedMonth, setSelectedMonth] = useState('');
  const [availableMonths, setAvailableMonths] = useState([]);
  const [monthlyBreakdown, setMonthlyBreakdown] = useState({ Income: {}, Expenses: {}, Savings: {} });
  const [barChartType, setBarChartType] = useState('Income');
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    loadData();
  }, [projectId]);

  useEffect(() => {
    if (selectedMonth) {
      loadMonthlyBreakdown();
    }
  }, [selectedMonth]);

  const loadData = async () => {
    try {
      const [transactionsRes, summaryRes] = await Promise.all([
        api.getTransactions(projectId),
        api.getSummary(projectId)
      ]);

      setTransactions(transactionsRes.data.transactions);
      setSummary(summaryRes.data.summary);

      // Extract available months
      const months = Object.keys(summaryRes.data.summary).sort();
      setAvailableMonths(months);

      // Set current month as default
      const currentDate = new Date();
      const currentMonth = `${String(currentDate.getMonth() + 1).padStart(2, '0')}/${currentDate.getFullYear()}`;
      setSelectedMonth(months.includes(currentMonth) ? currentMonth : months[months.length - 1] || currentMonth);

      setLoading(false);
    } catch (err) {
      console.error('Failed to load data:', err);
      setLoading(false);
    }
  };

  const loadMonthlyBreakdown = async () => {
    try {
      const [incomeRes, expensesRes, savingsRes] = await Promise.all([
        api.getBreakdown(projectId, selectedMonth, 'Income'),
        api.getBreakdown(projectId, selectedMonth, 'Expenses'),
        api.getBreakdown(projectId, selectedMonth, 'Savings')
      ]);

      setMonthlyBreakdown({
        Income: incomeRes.data.breakdown,
        Expenses: expensesRes.data.breakdown,
        Savings: savingsRes.data.breakdown
      });
    } catch (err) {
      console.error('Failed to load breakdown:', err);
    }
  };

  const handleDeleteProject = async () => {
    try {
      await api.deleteProject(projectId);
      onBack();
    } catch (err) {
      alert('Failed to delete project');
    }
  };

  const getMonthTotal = (type) => {
    if (!selectedMonth || !summary[selectedMonth]) return 0;
    return summary[selectedMonth][type] || 0;
  };

  const getNetChange = () => {
    const income = getMonthTotal('Income');
    const expenses = getMonthTotal('Expenses');
    return income - expenses;
  };

  const createPieChartData = (type) => {
    const data = monthlyBreakdown[type];
    const categories = Object.keys(data);

    if (categories.length === 0) {
      return null;
    }

    const colors = {
      Income: ['#28a745', '#34ce57', '#5dd879', '#86e29b', '#afecbd'],
      Expenses: ['#dc3545', '#e35462', '#ea737f', '#f1929c', '#f8b1b9'],
      Savings: ['#17a2b8', '#35b5ca', '#53c8dc', '#71dbee', '#8feeee']
    };

    return {
      labels: categories,
      datasets: [
        {
          data: categories.map((cat) => data[cat]),
          backgroundColor: colors[type],
          borderWidth: 2,
          borderColor: '#fff'
        }
      ]
    };
  };

  const createBarChartData = () => {
    const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    const currentYear = selectedMonth ? selectedMonth.split('/')[1] : new Date().getFullYear();

    const data = months.map((month) => {
      const key = `${month}/${currentYear}`;
      return summary[key] ? summary[key][barChartType] || 0 : 0;
    });

    const selectedMonthIndex = selectedMonth ? parseInt(selectedMonth.split('/')[0]) - 1 : -1;

    const backgroundColors = data.map((_, index) =>
      index === selectedMonthIndex ? '#667eea' : '#b0b9ff'
    );

    return {
      labels,
      datasets: [
        {
          label: barChartType,
          data,
          backgroundColor: backgroundColors,
          borderColor: '#667eea',
          borderWidth: 1
        }
      ]
    };
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 10,
          font: {
            size: 11
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: $${value.toFixed(2)}`;
          }
        }
      }
    }
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${barChartType}: $${context.parsed.y.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `$${value}`
        }
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2>{projectName}</h2>
            <p style={{ color: '#666' }}>Budget Dashboard</p>
          </div>
          <button className="btn btn-secondary" onClick={onBack}>
            ← Back to Projects
          </button>
        </div>

        <div className="dashboard-nav">
          <button className="btn btn-primary" onClick={() => onNavigate('data-entry')}>
            + Add Data Manually
          </button>
          <button className="btn btn-primary" onClick={() => onNavigate('file-upload')}>
            📁 Upload File
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('edit-categories')}>
            ⚙️ Edit Categories
          </button>
          <button
            className="btn btn-danger"
            onClick={() => setShowDeleteConfirm(true)}
          >
            🗑️ Delete Project
          </button>
        </div>

        <div className="metrics">
          <div className="metric-box">
            <h3>Total Transactions</h3>
            <p>{transactions.length}</p>
          </div>
        </div>

        <div className="input-group">
          <label>Select Month</label>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              style={{ maxWidth: '200px' }}
            >
              {availableMonths.map((month) => (
                <option key={month} value={month}>
                  {month}
                </option>
              ))}
            </select>
            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('manual-entry')}
              style={{ whiteSpace: 'nowrap' }}
            >
              Manage Data
            </button>
          </div>
        </div>

        {selectedMonth && (
          <>
            <div className="breakdown">
              <div className="breakdown-item income">
                <h4>Total Income</h4>
                <p>${getMonthTotal('Income').toFixed(2)}</p>
              </div>
              <div className="breakdown-item expenses">
                <h4>Total Expenses</h4>
                <p>${getMonthTotal('Expenses').toFixed(2)}</p>
              </div>
              <div className="breakdown-item savings">
                <h4>Total Savings</h4>
                <p>${getMonthTotal('Savings').toFixed(2)}</p>
              </div>
            </div>

            <div className="metric-box" style={{ marginTop: '20px' }}>
              <h3>Net Change for {selectedMonth}</h3>
              <p style={{ color: getNetChange() >= 0 ? '#4ade80' : '#f87171' }}>
                {getNetChange() >= 0 ? '+' : ''}${getNetChange().toFixed(2)}
              </p>
            </div>

            <h3 style={{ marginTop: '30px', marginBottom: '20px' }}>Category Breakdown</h3>
            <div className="pie-charts">
              {['Income', 'Expenses', 'Savings'].map((type) => {
                const chartData = createPieChartData(type);
                return (
                  <div key={type} className="chart-container">
                    <h3>{type}</h3>
                    {chartData ? (
                      <Pie data={chartData} options={pieChartOptions} />
                    ) : (
                      <p style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
                        No {type.toLowerCase()} data for this month
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="bar-chart-container">
              <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>Monthly Overview</h3>

              <div className="chart-controls">
                {['Income', 'Expenses', 'Savings'].map((type) => (
                  <button
                    key={type}
                    className={`toggle-btn ${barChartType === type ? 'active' : ''}`}
                    onClick={() => setBarChartType(type)}
                  >
                    {type}
                  </button>
                ))}
              </div>

              <Bar data={createBarChartData()} options={barChartOptions} />
            </div>
          </>
        )}
      </div>

      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Project</h2>
            <p>
              Are you sure you want to delete "{projectName}"? This will permanently delete all
              transactions and categories associated with this project.
            </p>
            <div className="modal-actions">
              <button
                className="btn btn-danger"
                onClick={handleDeleteProject}
              >
                Yes, Delete
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
