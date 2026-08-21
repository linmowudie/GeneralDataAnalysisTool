import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntApp, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { sentriTheme } from './theme';
import { SessionProvider } from './context/SessionContext';
import AppLayout from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import RouteGuard from './components/common/RouteGuard';

const Dashboard = lazy(() => import('./modules/dashboard/Dashboard'));
const DataImportModule = lazy(() => import('./modules/data-import/DataImportModule'));
const DataPreviewModule = lazy(() => import('./modules/data-preview/DataPreviewModule'));
const DataCleaningModule = lazy(() => import('./modules/data-cleaning/DataCleaningModule'));
const DataAnalysisModule = lazy(() => import('./modules/data-analysis/DataAnalysisModule'));
const AgentPage = lazy(() => import('./modules/agent/AgentPage'));
const VisualizationModule = lazy(() => import('./modules/visualization/VisualizationModule'));
const ReportingModule = lazy(() => import('./modules/reporting/ReportingModule'));

const PageLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
    <Spin size="large" tip="加载中..." />
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider theme={sentriTheme} locale={zhCN}>
        <AntApp>
          <SessionProvider>
            <Routes>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
                <Route path="/import" element={<Suspense fallback={<PageLoader />}><DataImportModule /></Suspense>} />
                <Route path="/preview" element={<RouteGuard requireAllOf={['import']}><Suspense fallback={<PageLoader />}><DataPreviewModule /></Suspense></RouteGuard>} />
                <Route path="/cleaning" element={<RouteGuard requireAllOf={['import']}><Suspense fallback={<PageLoader />}><DataCleaningModule /></Suspense></RouteGuard>} />
                <Route path="/analysis" element={<RouteGuard requireAnyOf={['cleaning', 'import']}><Suspense fallback={<PageLoader />}><DataAnalysisModule /></Suspense></RouteGuard>} />
                <Route path="/agent" element={<Suspense fallback={<PageLoader />}><AgentPage /></Suspense>} />
                <Route path="/visualization" element={<RouteGuard requireAllOf={['analysis']}><Suspense fallback={<PageLoader />}><VisualizationModule /></Suspense></RouteGuard>} />
                <Route path="/report" element={<RouteGuard requireAllOf={['analysis']}><Suspense fallback={<PageLoader />}><ReportingModule /></Suspense></RouteGuard>} />
                <Route path="*" element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
              </Route>
            </Routes>
          </SessionProvider>
        </AntApp>
      </ConfigProvider>
    </ErrorBoundary>
  );
}

export default App;
