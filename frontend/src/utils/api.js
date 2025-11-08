import axios from 'axios';

const API_BASE_URL = '/api';

const api = {
  // Projects
  getProjects: () => axios.get(`${API_BASE_URL}/projects`),
  createProject: (name) => axios.post(`${API_BASE_URL}/projects`, { name }),
  getProject: (projectId) => axios.get(`${API_BASE_URL}/projects/${projectId}`),
  deleteProject: (projectId) => axios.delete(`${API_BASE_URL}/projects/${projectId}`),

  // Categories
  getCategories: (projectId, type) => {
    const params = type ? { type } : {};
    return axios.get(`${API_BASE_URL}/projects/${projectId}/categories`, { params });
  },
  addCategory: (projectId, name, type) =>
    axios.post(`${API_BASE_URL}/projects/${projectId}/categories`, { name, type }),
  deleteCategory: (categoryId) => axios.delete(`${API_BASE_URL}/categories/${categoryId}`),

  // Transactions
  getTransactions: (projectId, month) => {
    const params = month ? { month } : {};
    return axios.get(`${API_BASE_URL}/projects/${projectId}/transactions`, { params });
  },
  addTransaction: (projectId, transaction) =>
    axios.post(`${API_BASE_URL}/projects/${projectId}/transactions`, transaction),
  addTransactionsBatch: (projectId, transactions) =>
    axios.post(`${API_BASE_URL}/projects/${projectId}/transactions/batch`, { transactions }),
  updateTransaction: (transactionId, data) =>
    axios.put(`${API_BASE_URL}/transactions/${transactionId}`, data),
  deleteTransaction: (transactionId) => axios.delete(`${API_BASE_URL}/transactions/${transactionId}`),

  // Analytics
  getSummary: (projectId) => axios.get(`${API_BASE_URL}/projects/${projectId}/summary`),
  getBreakdown: (projectId, month, type) =>
    axios.get(`${API_BASE_URL}/projects/${projectId}/breakdown`, { params: { month, type } }),

  // AI Extraction
  extractData: (file, fileType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileType', fileType);
    return axios.post(`${API_BASE_URL}/extract-data`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  // Health check
  healthCheck: () => axios.get(`${API_BASE_URL}/health`)
};

export default api;
