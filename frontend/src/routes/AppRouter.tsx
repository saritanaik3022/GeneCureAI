import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Lazy loading of all 12 multi-page routes for performance
const DashboardPage = lazy(() =>
  import('../pages/DashboardPage').then((m) => ({ default: m.DashboardPage }))
);
const DesignStudioPage = lazy(() =>
  import('../pages/DesignStudioPage').then((m) => ({ default: m.DesignStudioPage }))
);
const AnalysisPipelinePage = lazy(() =>
  import('../pages/AnalysisPipelinePage').then((m) => ({ default: m.AnalysisPipelinePage }))
);
const GRNACandidatesPage = lazy(() =>
  import('../pages/GRNACandidatesPage').then((m) => ({ default: m.GRNACandidatesPage }))
);
const OffTargetPage = lazy(() =>
  import('../pages/OffTargetPage').then((m) => ({ default: m.OffTargetPage }))
);
const TOPSISRankingPage = lazy(() =>
  import('../pages/TOPSISRankingPage').then((m) => ({ default: m.TOPSISRankingPage }))
);
const RankedGuidesPage = lazy(() =>
  import('../pages/RankedGuidesPage').then((m) => ({ default: m.RankedGuidesPage }))
);
const CompareGuidesPage = lazy(() =>
  import('../pages/CompareGuidesPage').then((m) => ({ default: m.CompareGuidesPage }))
);
const ModelPerformancePage = lazy(() =>
  import('../pages/ModelPerformancePage').then((m) => ({ default: m.ModelPerformancePage }))
);
const AnalysisHistoryPage = lazy(() =>
  import('../pages/AnalysisHistoryPage').then((m) => ({ default: m.AnalysisHistoryPage }))
);
const ReportsPage = lazy(() =>
  import('../pages/ReportsPage').then((m) => ({ default: m.ReportsPage }))
);
const MethodologyPage = lazy(() =>
  import('../pages/MethodologyPage').then((m) => ({ default: m.MethodologyPage }))
);
const AboutPage = lazy(() =>
  import('../pages/AboutPage').then((m) => ({ default: m.AboutPage }))
);

const PageLoader: React.FC = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <div className="flex flex-col items-center gap-3">
      <div className="w-8 h-8 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
      <span className="text-xs font-mono text-slate-400">Loading research module...</span>
    </div>
  </div>
);

export const AppRouter: React.FC = () => {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/design-studio" element={<DesignStudioPage />} />
        <Route path="/analysis-pipeline" element={<AnalysisPipelinePage />} />
        <Route path="/ranked-guides" element={<RankedGuidesPage />} />
        <Route path="/grna-candidates" element={<GRNACandidatesPage />} />
        <Route path="/off-target" element={<OffTargetPage />} />
        <Route path="/topsis-ranking" element={<TOPSISRankingPage />} />
        <Route path="/compare-guides" element={<CompareGuidesPage />} />
        <Route path="/model-performance" element={<ModelPerformancePage />} />
        <Route path="/analysis-history" element={<AnalysisHistoryPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/methodology" element={<MethodologyPage />} />
        <Route path="/about" element={<AboutPage />} />

        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
};
