// ============================================================
// Gene-Cure AI — API Service Layer
// All endpoints connect to FastAPI backend.
// ============================================================

import type {
  HealthResponse,
  CancerGene,
  GuideRNA,
  GuideDesignScanResponse,
  OnTargetPredictResponse,
  OffTargetResponse,
  TOPSISRankedItem,
  PipelineExecutionResponse,
  TOPSISWeights,
} from '../types';

// Resolve configured backend base URL from environment (e.g. Vercel Production)
// If VITE_API_URL is defined, use it; otherwise fall back to relative path for Vite dev proxy.
const rawApiUrl = (import.meta.env.VITE_API_URL || '').trim();
// Strip trailing slashes to prevent duplicate slashes
const BACKEND_BASE = rawApiUrl ? rawApiUrl.replace(/\/+$/, '') : '';

// Safely construct API base URL (avoid duplicate /api/v1 if VITE_API_URL already includes it)
export const API_BASE = BACKEND_BASE
  ? (BACKEND_BASE.endsWith('/api/v1') ? BACKEND_BASE : `${BACKEND_BASE}/api/v1`)
  : '/api/v1';

// ---- Core fetch helper ----

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text().catch(() => 'Unknown error');
    throw new Error(`API error ${response.status} on ${url}: ${text}`);
  }
  return response.json() as Promise<T>;
}

// ---- Health ----

export const fetchHealthStatus = async (): Promise<HealthResponse> => {
  // If a production backend URL is configured (VITE_API_URL exists), query the production backend endpoints.
  // In local development (VITE_API_URL not set), test relative proxy paths and local dev fallbacks.
  const candidateUrls = BACKEND_BASE
    ? [
        `${BACKEND_BASE}/health`,
        `${BACKEND_BASE}/api/health`,
        `${API_BASE}/health`,
      ]
    : [
        '/health',
        '/api/health',
        `${API_BASE}/health`,
        'http://127.0.0.1:8000/health',
        'http://127.0.0.1:8000/api/health',
      ];
  let lastError: any = null;

  for (const url of candidateUrls) {
    try {
      const data = await apiFetch<any>(url);
      if (data && (data.status === 'ok' || data.status === 'healthy' || data.status === 'SUCCESS' || !!data.status)) {
        return {
          status: data.status,
          service: data.service || 'gene-cure-ai',
          version: data.version || '1.0.0',
          execution_mode: data.execution_mode || 'REAL_MODE',
          database_connected: data.database_connected ?? true,
          grch38_available: data.grch38_available ?? true,
          models_loaded: data.models_loaded ?? true,
          ...data,
        };
      }
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error('Backend health check failed');
};

// ---- Cancer Genes (Stage 1) ----

export const fetchCancerGenes = (cancerType?: string): Promise<CancerGene[]> => {
  const url = cancerType
    ? `${API_BASE}/cancer-genes?cancer_type=${encodeURIComponent(cancerType)}`
    : `${API_BASE}/cancer-genes`;
  return apiFetch<CancerGene[]>(url);
};

export const fetchCancerGeneDetail = (symbol: string): Promise<CancerGene> =>
  apiFetch<CancerGene>(`${API_BASE}/cancer-genes/${symbol}`);

// ---- Guide RNA Scan (Stage 2) ----

export interface GuideScanRequest {
  gene_symbol?: string;
  sequence?: string;
  gc_min?: number;
  gc_max?: number;
  exclude_poly_t?: boolean;
}

export type GuideScanResult = {
  candidates: GuideRNA[];
  metadata?: GuideDesignScanResponse;
};

export const scanGuides = async (req: GuideScanRequest): Promise<GuideScanResult> => {
  const data = await apiFetch<GuideDesignScanResponse | GuideRNA[]>(`${API_BASE}/guide-design/scan`, {
    method: 'POST',
    body: JSON.stringify(req),
  });

  if (Array.isArray(data)) {
    return { candidates: data };
  } else if (data && Array.isArray(data.candidates)) {
    return { candidates: data.candidates, metadata: data };
  }
  return { candidates: [] };
};

// ---- On-Target Prediction (Stage 3) ----

export interface OnTargetRequest {
  guides_30nt: string[];
}

export const predictOnTarget = (req: OnTargetRequest): Promise<OnTargetPredictResponse> =>
  apiFetch<OnTargetPredictResponse>(`${API_BASE}/on-target/predict`, {
    method: 'POST',
    body: JSON.stringify(req),
  });

export interface ModelPerformanceResponse {
  status: 'READY' | 'MODEL_NOT_READY';
  message?: string;
  metadata?: {
    model_version: string;
    feature_version: string;
    dataset_name: string;
    dataset_rows: number;
    train_rows: number;
    validation_rows: number;
    test_rows: number;
    training_date: string;
    features_dim: number;
    hybrid_features_dim: number;
    artifacts: {
      cnn: string;
      xgboost: string;
      hybrid: string;
    };
    metrics: {
      CNN: {
        spearman_rho: number;
        pearson_r: number;
        mae: number;
        rmse: number;
        r2: number;
      };
      XGBoost: {
        spearman_rho: number;
        pearson_r: number;
        mae: number;
        rmse: number;
        r2: number;
      };
      Hybrid: {
        spearman_rho: number;
        pearson_r: number;
        mae: number;
        rmse: number;
        r2: number;
      };
    };
  };
}

export const fetchModelPerformance = (): Promise<ModelPerformanceResponse> =>
  apiFetch<ModelPerformanceResponse>(`${API_BASE}/on-target/performance`);

// ---- Off-Target Analysis (Stage 4) ----

export interface OffTargetRequest {
  guide_sequences: string[];
  tool_preference?: 'bowtie2' | 'blast';
}

export const analyzeOffTarget = (req: OffTargetRequest): Promise<OffTargetResponse> =>
  apiFetch<OffTargetResponse>(`${API_BASE}/off-target/analyze`, {
    method: 'POST',
    body: JSON.stringify(req),
  });

// ---- TOPSIS Ranking (Stage 5) ----

export interface TOPSISRequest {
  run_id?: string;
  weights?: TOPSISWeights;
}

export const fetchTopsisRanking = (req: TOPSISRequest): Promise<{ ranked_guides: TOPSISRankedItem[] }> =>
  apiFetch<{ ranked_guides: TOPSISRankedItem[] }>(`${API_BASE}/topsis/rank`, {
    method: 'POST',
    body: JSON.stringify(req),
  });

// ---- Full Pipeline Execution ----

export interface PipelineRequest {
  gene_symbol: string;
  cancer_type?: string;
  custom_sequence?: string;
  execution_mode?: 'REAL_MODE' | 'DEMO_MODE';
  top_n?: number;
  weights?: TOPSISWeights;
}

export const executePipeline = (req: PipelineRequest): Promise<PipelineExecutionResponse> =>
  apiFetch<PipelineExecutionResponse>(`${API_BASE}/pipeline/execute`, {
    method: 'POST',
    body: JSON.stringify(req),
  });
