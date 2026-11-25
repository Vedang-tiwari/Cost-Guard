import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { DashboardLayout } from './layouts/DashboardLayout';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { BenchmarksPage } from './pages/BenchmarksPage';
import { BudgetsPage } from './pages/BudgetsPage';
import { CostAnalyticsPage } from './pages/CostAnalyticsPage';
import { LoginPage } from './pages/LoginPage';
import { ModelsPage } from './pages/ModelsPage';
import { OptimizationPage } from './pages/OptimizationPage';
import { OverviewPage } from './pages/OverviewPage';
import { PlaygroundPage } from './pages/PlaygroundPage';
import { RegisterPage } from './pages/RegisterPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500">
        Loading Cost Guard session...
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<OverviewPage />} />
        <Route path="playground" element={<PlaygroundPage />} />
        <Route path="costs" element={<CostAnalyticsPage />} />
        <Route path="models" element={<ModelsPage />} />
        <Route path="optimization" element={<OptimizationPage />} />
        <Route path="budgets" element={<BudgetsPage />} />
        <Route path="benchmarks" element={<BenchmarksPage />} />
        <Route path="applications" element={<ApplicationsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
