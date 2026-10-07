import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Topbar from './components/layout/Topbar';
import { ToastProvider } from './hooks/useToast';

// Pages
import UploadStatement from './pages/UploadStatement';
import Transactions from './pages/Transactions';
import LedgerMappings from './pages/LedgerMappings';
import TallyPrime from './pages/TallyPrime';

function MainLayout() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-wrapper">
        <Topbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadStatement />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/tally" element={<TallyPrime />} />
            <Route path="/mappings" element={<LedgerMappings />} />
            <Route path="*" element={<Navigate to="/upload" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <MainLayout />
      </ToastProvider>
    </BrowserRouter>
  );
}
