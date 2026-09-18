// ============================================================
// Gene-Cure AI — TypeScript Type Definitions
// ============================================================

export type ExecutionMode = 'REAL_MODE' | 'DEMO_MODE';

export type PipelineStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'COMPLETED'
  | 'FAILED'
  | 'GENOME_NOT_AVAILABLE';

export type PipelineStage =
  | 'IDLE'
  | 'GENE_SEQUENCE'
  | 'GRNA_IDENTIFICATION'
  | 'ON_TARGET'
  | 'OFF_TARGET'
  | 'RANKING'
  | 'COMPLETED'
  | 'FAILED';

export type ResourceStatus =
  | 'READY'
  | 'NOT_READY'
  | 'NOT_AVAILABLE'
  | 'CHECKING'
  | 'ERROR';

// ---- Health / System ----

export interface HealthResponse {
  status: string;
  service?: string;
  version?: string;
  execution_mode?: ExecutionMode;
  database_connected?: boolean;
  grch38_available?: boolean;
  gencode_available?: boolean;
  genome_index_available?: boolean;
  models_loaded?: boolean;
}

// ---- Cancer Gene Registry ----

export interface CancerGene {
  id: string;
  symbol: string;
  name: string;
  cancer_types: string[];
  ncbi_gene_id: string;
  ensembl_id: string;
  hgnc_id: string;
  chromosome: string;
  strand: '+' | '-';
  genomic_start: number;
  genomic_end: number;
  canonical_transcript_id: string;
  cancer_relevance_summary: string;
  depmap_dependency_score?: number;
  cds_length?: number;
  cds_sequence?: string;
  full_transcript_sequence?: string;
}

// ---- Guide RNA ----

export interface GuideRNA {
  id: string;
  protospacer_sequence: string;
  pam_sequence: string;
  context_30nt_sequence: string;
  strand: '+' | '-';
  genomic_start: number;
  genomic_end: number;
  exon_number?: number;
  gc_percentage: number;
  has_poly_t_terminator: boolean;
  self_complementarity_score: number;
  gene_id?: string;
  chromosome?: string;
  reference_assembly?: string;
  annotation_source?: string;
  sequence_type?: string;
  cleavage_coordinate?: number;
}

export interface GuideDesignScanResponse {
  mode: string;
  gene: string;
  gene_id: string;
  genome: string;
  annotation: string;
  transcript: string;
  chromosome: string;
  strand: string;
  sequence_type: string;
  total_exons_scanned: number;
  cds_length_scanned: number;
  candidate_count: number;
  candidates: GuideRNA[];
  filter_summary?: {
    total_raw_pams?: number;
    passed_filters?: number;
    failed_gc?: number;
    failed_poly_t?: number;
    failed_self_comp?: number;
  };
}

// ---- On-Target Prediction ----

export interface OnTargetPrediction {
  sequence_30nt: string;
  guide_20nt: string;
  pam: string;
  cnn_score: number;
  xgboost_score: number;
  ensemble_score: number;
  confidence_tier: 'High' | 'Moderate' | 'Low';
  top_positive_features: string[];
  top_negative_features: string[];
}

export interface OnTargetPredictResponse {
  total_evaluated: number;
  predictions: OnTargetPrediction[];
  model_version: string;
  execution_mode: ExecutionMode;
}

// ---- Off-Target Analysis ----

export interface OffTargetSite {
  chromosome: string;
  position: number;
  strand: '+' | '-';
  sequence: string;
  pam: string;
  mismatches: number;
  mismatch_positions: number[];
  cfd_score: number;
  annotation: string;
}

export interface SingleGuideOffTarget {
  guide_sequence: string;
  total_off_targets: number;
  mismatch_counts: Record<string, number>;
  cumulative_cfd_score: number;
  specificity_score: number;
  normalized_safety_score: number;
  sites: OffTargetSite[];
}

export interface OffTargetResponse {
  reference_genome: string;
  search_tool: string;
  execution_mode: ExecutionMode;
  results: SingleGuideOffTarget[];
}

// ---- TOPSIS Ranking ----

export interface TOPSISWeights {
  w_on_target: number;      // default 0.35
  w_off_target: number;     // default 0.30
  w_cancer_relevance: number; // default 0.20
  w_gc_optimality: number;  // default 0.15
}

export interface TOPSISRankedItem {
  rank: number;
  guide_id: string;
  protospacer_sequence: string;
  pam: string;
  strand?: string;
  chromosome?: string;
  genomic_start?: number;
  genomic_end?: number;
  exon_number?: number;
  gc_content?: number;
  gc_percentage?: number;
  closeness_score: number;
  distance_positive_ideal: number;
  distance_negative_ideal: number;
  on_target_criterion: number;
  off_target_criterion: number;
  cancer_relevance_criterion: number;
  gc_optimality_criterion: number;
  context_30nt?: string;
  cleavage_coordinate?: number;
}

// ---- Pipeline ----

export interface StageSummary {
  stage_number: number;
  stage_name: string;
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'SKIPPED';
  summary: string;
  duration_ms: number;
}

export interface PipelineExecutionResponse {
  run_id: string;
  gene_symbol: string;
  cancer_type?: string;
  execution_mode: ExecutionMode;
  status: PipelineStatus;
  total_guides_scanned: number;
  ranked_count?: number;
  ranked_guides: TOPSISRankedItem[];
  stage_summaries: StageSummary[];
  custom_sequence?: string;
  total_execution_time_ms: number;
}

// ---- Model Metrics (Phase 3 - not yet trained) ----

export interface ModelMetrics {
  spearman_correlation: number | null;
  pearson_correlation: number | null;
  mae: number | null;
  rmse: number | null;
  r_squared: number | null;
  roc_auc: number | null;
  model_version: string;
  training_dataset: string;
  test_set_size: number | null;
  trained: boolean;
}

// ---- System Resource Status ----

export interface SystemStatus {
  backend: ResourceStatus;
  database: ResourceStatus;
  grch38: ResourceStatus;
  gencode: ResourceStatus;
  bowtie2: ResourceStatus;
  doench_dataset: ResourceStatus;
  cnn_model: ResourceStatus;
  xgboost_model: ResourceStatus;
}

// ---- Analysis History ----

export interface AnalysisRun {
  run_id: string;
  gene_symbol: string;
  cancer_type: string;
  execution_mode: ExecutionMode;
  status: PipelineStatus;
  created_at: string;
  total_guides_scanned: number;
  top_guide?: string;
  top_topsis_score?: number;
}

// ---- Cancer Type Gene Mapping ----

export const CANCER_GENE_MAP: Record<string, string[]> = {
  'Breast cancer': ['BRCA1', 'HER2', 'TP53'],
  'Lung cancer': ['EGFR', 'KRAS', 'ALK'],
  'Liver cancer': ['CTNNB1', 'AXIN1', 'TERT'],
} as const;

export const GENE_FULL_NAMES: Record<string, string> = {
  BRCA1: 'Breast Cancer 1 (BRCA1)',
  HER2: 'Erb-B2 Receptor Tyrosine Kinase 2 (ERBB2 / HER2)',
  TP53: 'Tumor Protein P53 (TP53)',
  EGFR: 'Epidermal Growth Factor Receptor (EGFR)',
  KRAS: 'Kirsten Rat Sarcoma Virus (KRAS)',
  ALK: 'Anaplastic Lymphoma Kinase (ALK)',
  CTNNB1: 'Catenin Beta 1 (CTNNB1)',
  AXIN1: 'Axis Inhibition Protein 1 (AXIN1)',
  TERT: 'Telomerase Reverse Transcriptase (TERT)',
};

export const ALL_TARGET_GENES = ['BRCA1', 'HER2', 'TP53', 'EGFR', 'KRAS', 'ALK', 'CTNNB1', 'AXIN1', 'TERT'] as const;

export type TargetGene = typeof ALL_TARGET_GENES[number];
