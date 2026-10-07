import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

// Response error interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const BankAPI = {
  uploadStatement: (formData) => api.post('/bank/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  processSampleInvoice: () => api.post('/bank/sample-invoice'),
};

export const TransactionAPI = {
  getTransactions: (params) => api.get('/transactions', { params }),
  getTransaction: (id) => api.get(`/transactions/${id}`),
  approveTransaction: (id, data) => api.post(`/transactions/${id}/approve`, data),
  bulkApprove: (ids) => api.post('/transactions/bulk-approve', { transaction_ids: ids }),
};

export const TallyAPI = {
  getStatus: () => api.get('/tally/status'),
  testConnection: () => api.post('/tally/test-connection'),
  postTransaction: (id) => api.post(`/tally/post/${id}`),
  postBulk: (ids) => api.post('/tally/post-bulk', { transaction_ids: ids }),
  getHistory: () => api.get('/tally/history'),
  getLedgers: () => api.get('/tally/ledgers'),
};

export const MappingAPI = {
  getMappings: () => api.get('/mappings'),
  createMapping: (data) => api.post('/mappings', data),
  updateMapping: (id, data) => api.put(`/mappings/${id}`, data),
  deleteMapping: (id) => api.delete(`/mappings/${id}`),
  testMapping: (data) => api.post('/mappings/test', data),
};

export default api;
