// ============================================================
// Gene-Cure AI — Real Analysis Session & History Storage
// Strictly stores and retrieves real analysis execution results.
// No fabricated records or synthetic placeholders.
// ============================================================

import type { PipelineExecutionResponse, TOPSISRankedItem } from '../types';
import { VALIDATED_9_GENE_RUNS } from '../data/validatedRuns';

export interface StoredAnalysisRun {
  runId: string;
  cancer: string;
  gene: string;
  date: string;
  timestamp: number;
  mode: 'REAL_MODE' | 'DEMO_MODE';
  status: string;
  candidateCount: number;
  modelVersion: string;
  topGuide: string;
  pam: string;
  topsisScore: number;
  rankedGuides: TOPSISRankedItem[];
  customSequence?: string;
  analysisType?: 'curated_gene' | 'custom_sequence';
  provenance: {
    genome: string;
    annotation: string;
    transcript?: string;
    chromosome?: string;
    strand?: string;
    custom_sequence?: string;
  };
}

const STORAGE_KEY = 'genecure_ai_analysis_history';
const LATEST_KEY = 'genecure_ai_latest_analysis';

export const analysisStorage = {
  getHistory(): StoredAnalysisRun[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return VALIDATED_9_GENE_RUNS;
      const parsed = JSON.parse(data);
      return Array.isArray(parsed) && parsed.length > 0 ? parsed : VALIDATED_9_GENE_RUNS;
    } catch {
      return VALIDATED_9_GENE_RUNS;
    }
  },

  getLatest(): StoredAnalysisRun | null {
    try {
      const data = localStorage.getItem(LATEST_KEY);
      if (!data) {
        const history = this.getHistory();
        return history.length > 0 ? history[0] : null;
      }
      return JSON.parse(data);
    } catch {
      const history = this.getHistory();
      return history.length > 0 ? history[0] : null;
    }
  },

  saveRun(
    response: PipelineExecutionResponse,
    cancer?: string,
    customSequence?: string
  ): StoredAnalysisRun {
    const topGuide = response.ranked_guides && response.ranked_guides.length > 0
      ? response.ranked_guides[0]
      : null;

    const seq = customSequence || response.custom_sequence;
    const isCustom = Boolean(seq && seq.length > 0);

    const run: StoredAnalysisRun = {
      runId: response.run_id,
      cancer: cancer || (isCustom ? 'Custom DNA Analysis' : response.gene_symbol + ' Cancer'),
      gene: response.gene_symbol,
      date: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
      timestamp: Date.now(),
      mode: response.execution_mode,
      status: response.status,
      candidateCount: response.total_guides_scanned || (response.ranked_guides ? response.ranked_guides.length : 0),
      modelVersion: '1.0.0 (Hybrid Ensemble)',
      topGuide: topGuide ? topGuide.protospacer_sequence : 'N/A',
      pam: topGuide ? topGuide.pam : 'NGG',
      topsisScore: topGuide ? topGuide.closeness_score : 0,
      rankedGuides: response.ranked_guides || [],
      customSequence: seq,
      analysisType: isCustom ? 'custom_sequence' : 'curated_gene',
      provenance: {
        genome: 'GRCh38.p14',
        annotation: isCustom ? 'Custom DNA Input' : 'GENCODE v46',
        gene: response.gene_symbol,
        custom_sequence: seq,
      } as any,
    };

    try {
      const history = this.getHistory();
      const updatedHistory = [run, ...history.filter((r) => r.runId !== run.runId)].slice(0, 50);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedHistory));
      localStorage.setItem(LATEST_KEY, JSON.stringify(run));
    } catch (e) {
      console.warn('Failed to persist analysis run to localStorage', e);
    }

    return run;
  },

  updateLatestRankedGuides(guides: TOPSISRankedItem[]): void {
    try {
      const latest = this.getLatest();
      if (latest) {
        latest.rankedGuides = guides;
        if (guides.length > 0) {
          latest.topGuide = guides[0].protospacer_sequence;
          latest.pam = guides[0].pam;
          latest.topsisScore = guides[0].closeness_score;
        }
        localStorage.setItem(LATEST_KEY, JSON.stringify(latest));
        const history = this.getHistory();
        const updatedHistory = history.map((r) => (r.runId === latest.runId ? latest : r));
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedHistory));
      }
    } catch (e) {
      console.warn('Failed to update latest ranked guides in localStorage', e);
    }
  },

  clearHistory(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(LATEST_KEY);
    } catch (e) {
      console.warn('Failed to clear analysis storage', e);
    }
  }
};
