import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Boxes,
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  Award,
  Dna,
  Target,
  ShieldCheck,
  Scissors,
  Sparkles,
  CheckCircle,
  ChevronRight,
  ArrowRight,
  type LucideIcon,
} from 'lucide-react';
import { DNAScene } from '../components/three/DNAScene';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { WorkflowNavigationFooter } from '../components/common/WorkflowNavigationFooter';
import { fetchCancerGenes, fetchCancerGeneDetail, scanGuides } from '../services/api';
import { analysisStorage, StoredAnalysisRun } from '../services/analysisStorage';
import { useHealth } from '../hooks/useHealth';
import { CancerGene, PipelineStage, CANCER_GENE_MAP, GENE_FULL_NAMES, GuideRNA } from '../types';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';

// ─── 6 Exact Simulation Stages (Requirement 17) ──────────────────────────────
interface SimStage {
  id: PipelineStage;
  numStr: string;
  label: string;
  description: string;
  icon: LucideIcon;
  color: string;
  durationMs: number;
}

const SIM_STAGES: SimStage[] = [
  {
    id: 'GENE_SEQUENCE',
    numStr: '01',
    label: 'DNA Scanning',
    description: 'Scanning the target CDS sequence 5\' → 3\' across exonic coding regions for canonical SpCas9 5\'-NGG PAM sites.',
    icon: Dna,
    color: 'cyan',
    durationMs: 3200,
  },
  {
    id: 'GRNA_IDENTIFICATION',
    numStr: '02',
    label: 'PAM Detected',
    description: "SpCas9 recognises the 5'-NGG PAM on the target DNA strand at the validated genomic coordinate.",
    icon: Target,
    color: 'amber',
    durationMs: 2500,
  },
  {
    id: 'ON_TARGET',
    numStr: '03',
    label: 'Target Protospacer Recognized',
    description: 'The 20-nt target protospacer adjacent to the PAM is identified and mapped on the sense strand.',
    icon: Sparkles,
    color: 'cyan',
    durationMs: 2500,
  },
  {
    id: 'OFF_TARGET',
    numStr: '04',
    label: 'Guide RNA Binding',
    description: 'Guide RNA approaches the target DNA strand, forming Watson-Crick complementary base-pairing with the protospacer.',
    icon: ShieldCheck,
    color: 'emerald',
    durationMs: 3000,
  },
  {
    id: 'RANKING',
    numStr: '05',
    label: 'SpCas9 Bound',
    description: 'The SpCas9 endonuclease ribonucleoprotein (RNP) complex envelops the guide-target heteroduplex.',
    icon: Boxes,
    color: 'indigo',
    durationMs: 2500,
  },
  {
    id: 'COMPLETED',
    numStr: '06',
    label: 'Predicted Cleavage',
    description: 'Predicted double-strand break (DSB) site at position −3 bp upstream of the PAM locus. Computational prediction only.',
    icon: Scissors,
    color: 'red',
    durationMs: 3000,
  },
];

export const DesignStudioPage: React.FC = () => {
  const { health } = useHealth();
  const location = useLocation();
  const navigate = useNavigate();
  const stateData = location.state as {
    selectedGuide?: any;
    geneSymbol?: string;
    cancerType?: string;
    customSequence?: string;
    autoStart?: boolean;
    runId?: string;
  } | undefined;

  // Retrieve stored latest analysis if available
  const [latestAnalysis] = useState<StoredAnalysisRun | null>(() => analysisStorage.getLatest());

  // Determine active target gene and cancer type
  const initialGeneSymbol = stateData?.geneSymbol || latestAnalysis?.gene || 'BRCA1';
  const initialCancerType = stateData?.cancerType || latestAnalysis?.cancer || 'Breast cancer';

  const isCustomRun = Boolean(
    stateData?.customSequence ||
    (latestAnalysis?.customSequence && latestAnalysis?.gene === initialGeneSymbol)
  );
  const customDnaSeq = stateData?.customSequence || latestAnalysis?.customSequence || '';

  const [selectedCancer, setSelectedCancer] = useState<string>(initialCancerType);
  const [selectedGeneSymbol, setSelectedGeneSymbol] = useState<string>(initialGeneSymbol);
  const [selectedGene, setSelectedGene] = useState<CancerGene | null>(null);

  // Candidate guides from real backend
  const [candidateGuides, setCandidateGuides] = useState<GuideRNA[]>([]);
  const [selectedGuideIndex, setSelectedGuideIndex] = useState<number>(0);
  const [loadingGuides, setLoadingGuides] = useState<boolean>(false);

  // Simulation state
  const [simStageIndex, setSimStageIndex] = useState<number>(-1); // -1 = idle
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [scanProgress, setScanProgress] = useState<number>(0);
  const [approachProgress, setApproachProgress] = useState<number>(0);
  const [simCompleted, setSimCompleted] = useState<boolean>(false);
  const [navigatingToTOPSIS, setNavigatingToTOPSIS] = useState<boolean>(false);
  const [fullCdsSequence, setFullCdsSequence] = useState<string>('');

  const animFrameRef = useRef<number | null>(null);
  const stageStartTimeRef = useRef<number>(0);
  const progressRef = useRef<{ scan: number; approach: number }>({ scan: 0, approach: 0 });
  const seqContainerRef = useRef<HTMLDivElement | null>(null);

  const currentStage = simStageIndex >= 0 ? SIM_STAGES[simStageIndex] : null;

  // Derive DNAScene booleans from current stage
  const activeStage: PipelineStage = currentStage?.id || 'IDLE';
  const isScanning = simStageIndex === 0;
  const highlightPam = simStageIndex >= 1;
  const highlightGuide = simStageIndex >= 2;
  const cas9Visible = simStageIndex >= 4;
  const cleavageActive = simStageIndex >= 5;

  // ── Fetch gene metadata & real CDS sequence ────────────────────────────────
  useEffect(() => {
    if (isCustomRun && customDnaSeq) {
      setFullCdsSequence(customDnaSeq);
      setSelectedGene({
        id: `gene-custom-${selectedGeneSymbol.toLowerCase()}`,
        symbol: selectedGeneSymbol,
        name: `Custom DNA Target Sequence (${selectedGeneSymbol})`,
        cancer_types: [selectedCancer],
        ncbi_gene_id: 'CUSTOM_NCBI_001',
        ensembl_id: 'CUSTOM_ENSG_001',
        hgnc_id: 'CUSTOM_HGNC_001',
        chromosome: 'chrCustom',
        strand: '+',
        genomic_start: 1,
        genomic_end: customDnaSeq.length,
        canonical_transcript_id: 'Custom_ENST_001',
        cancer_relevance_summary: 'User-provided custom DNA / FASTA nucleotide sequence for computational CRISPR-SpCas9 guide RNA analysis.',
        hallmark_roles: ['Custom Investigation'],
        description: 'User-provided custom DNA sequence.',
        cds_sequence: customDnaSeq,
        cds_length: customDnaSeq.length,
      } as unknown as CancerGene);
      return;
    }

    fetchCancerGeneDetail(selectedGeneSymbol)
      .then((geneDetail) => {
        setSelectedGene(geneDetail);
        if (geneDetail.cds_sequence) {
          setFullCdsSequence(geneDetail.cds_sequence);
        }
      })
      .catch(() => {
        fetchCancerGenes().then((data) => {
          const match = data.find((g) => g.symbol === selectedGeneSymbol);
          if (match) {
            setSelectedGene(match);
            if (match.cds_sequence) {
              setFullCdsSequence(match.cds_sequence);
            }
          }
        });
      });
  }, [selectedGeneSymbol, isCustomRun, customDnaSeq, selectedCancer]);

  // ── Fetch candidate guides from real backend ────────────────────────────────
  useEffect(() => {
    setLoadingGuides(true);
    if (isCustomRun && latestAnalysis?.rankedGuides && latestAnalysis.rankedGuides.length > 0) {
      const customGuides: GuideRNA[] = latestAnalysis.rankedGuides.map((g, idx) => ({
        id: g.guide_id || `gRNA-${selectedGeneSymbol}-${idx + 1}`,
        protospacer_sequence: g.protospacer_sequence,
        pam_sequence: g.pam || 'NGG',
        strand: (g.strand === '-' ? '-' : '+') as '+' | '-',
        exon_number: 1,
        gc_percentage: g.gc_content || 50.0,
        genomic_start: g.genomic_start || idx * 30 + 1,
        genomic_end: (g.genomic_start || idx * 30 + 1) + 23,
        cleavage_coordinate: (g.genomic_start || idx * 30 + 1) + 17,
        context_30nt_sequence: customDnaSeq ? customDnaSeq.slice(0, 30) : 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
        has_poly_t_terminator: false,
        self_complementarity_score: 0.0,
      }));
      setCandidateGuides(customGuides);
      if (stateData?.selectedGuide) {
        const matchIdx = customGuides.findIndex(
          (cg) => cg.protospacer_sequence === stateData.selectedGuide!.protospacer_sequence
        );
        setSelectedGuideIndex(matchIdx !== -1 ? matchIdx : 0);
      } else {
        setSelectedGuideIndex(0);
      }
      setLoadingGuides(false);
      return;
    }

    scanGuides({ gene_symbol: selectedGeneSymbol })
      .then((res) => {
        const guides = res.candidates.slice(0, 10);

        if (stateData?.selectedGuide) {
          const matchIdx = guides.findIndex(
            (g) => g.protospacer_sequence === stateData.selectedGuide!.protospacer_sequence
          );
          if (matchIdx !== -1) {
            setCandidateGuides(guides);
            setSelectedGuideIndex(matchIdx);
          } else {
            const passedGuide: GuideRNA = {
              id: stateData.selectedGuide.guide_id || `guide-${selectedGeneSymbol.toLowerCase()}-target`,
              protospacer_sequence: stateData.selectedGuide.protospacer_sequence,
              pam_sequence: stateData.selectedGuide.pam || stateData.selectedGuide.pam_sequence || 'NGG',
              strand: (stateData.selectedGuide.strand === '-' ? '-' : '+') as '+' | '-',
              exon_number: stateData.selectedGuide.exon_number || 1,
              gc_percentage: stateData.selectedGuide.gc_content || stateData.selectedGuide.gc_percentage || 50.0,
              genomic_start: stateData.selectedGuide.genomic_start || selectedGene?.genomic_start || 0,
              genomic_end: stateData.selectedGuide.genomic_end || (selectedGene?.genomic_start || 0) + 23,
              cleavage_coordinate: stateData.selectedGuide.cleavage_coordinate || (stateData.selectedGuide.genomic_start ? stateData.selectedGuide.genomic_start + 17 : undefined),
              context_30nt_sequence: stateData.selectedGuide.context_30nt || stateData.selectedGuide.context_30nt_sequence || selectedGene?.cds_sequence?.slice(0, 30) || 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
              has_poly_t_terminator: false,
              self_complementarity_score: 0.0,
            };
            setCandidateGuides([passedGuide, ...guides]);
            setSelectedGuideIndex(0);
          }
        } else {
          setCandidateGuides(guides);
          setSelectedGuideIndex(0);
        }
        setLoadingGuides(false);
      })
      .catch(() => {
        setLoadingGuides(false);
      });
  }, [selectedGeneSymbol, selectedGene, isCustomRun, customDnaSeq, latestAnalysis]);

  const selectedStateGuide = stateData?.selectedGuide;

  const currentGuide: GuideRNA = candidateGuides[selectedGuideIndex] || (selectedStateGuide ? {
    id: selectedStateGuide.guide_id || `guide-${selectedGeneSymbol.toLowerCase()}-01`,
    protospacer_sequence: selectedStateGuide.protospacer_sequence || (selectedGene?.cds_sequence ? selectedGene.cds_sequence.slice(0, 20) : 'ACGTACGTACGTACGTACGT'),
    pam_sequence: selectedStateGuide.pam || selectedStateGuide.pam_sequence || 'TGG',
    strand: (selectedStateGuide.strand === '-' ? '-' : '+') as '+' | '-',
    exon_number: selectedStateGuide.exon_number || 1,
    gc_percentage: selectedStateGuide.gc_content || selectedStateGuide.gc_percentage || 50.0,
    genomic_start: selectedStateGuide.genomic_start || selectedGene?.genomic_start || 0,
    genomic_end: selectedStateGuide.genomic_end || (selectedGene?.genomic_start || 0) + 23,
    cleavage_coordinate: selectedStateGuide.genomic_start ? selectedStateGuide.genomic_start + 17 : (selectedGene?.genomic_start ? selectedGene.genomic_start + 17 : undefined),
    context_30nt_sequence: selectedStateGuide.context_30nt_sequence || selectedGene?.cds_sequence?.slice(0, 30) || 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
    has_poly_t_terminator: false,
    self_complementarity_score: 0.0,
  } : {
    id: `guide-${selectedGeneSymbol.toLowerCase()}-01`,
    protospacer_sequence: selectedGene?.cds_sequence ? selectedGene.cds_sequence.slice(0, 20) : 'ACGTACGTACGTACGTACGT',
    pam_sequence: 'TGG',
    strand: '+' as const,
    exon_number: 1,
    gc_percentage: 50.0,
    genomic_start: selectedGene?.genomic_start || 0,
    genomic_end: (selectedGene?.genomic_start || 0) + 23,
    cleavage_coordinate: selectedGene?.genomic_start ? selectedGene.genomic_start + 17 : undefined,
    context_30nt_sequence: selectedGene?.cds_sequence ? selectedGene.cds_sequence.slice(0, 30) : 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
    has_poly_t_terminator: false,
    self_complementarity_score: 0.0,
  });

  function reverseComplement(seq: string): string {
    const comp: Record<string, string> = { A: 'T', T: 'A', G: 'C', C: 'G', N: 'N', a: 't', t: 'a', g: 'c', c: 'g', n: 'n' };
    return seq.split('').reverse().map((c) => comp[c] || c).join('');
  }

  const cdsDisplay = selectedGene?.cds_sequence || fullCdsSequence || '';

  // ── Find exact protospacer and PAM indices within full CDS ─────────────────
  const targetCoords = useMemo(() => {
    const cds = cdsDisplay.toUpperCase();
    const proto = (currentGuide.protospacer_sequence || '').toUpperCase();

    if (!cds || !proto) {
      return { protoStart: -1, protoEnd: -1, pamStart: -1, pamEnd: -1, isSense: true, matchSeq: proto };
    }

    // 1. Exact forward search in CDS
    let idx = cds.indexOf(proto);
    if (idx !== -1) {
      return {
        protoStart: idx,
        protoEnd: idx + 20,
        pamStart: idx + 20,
        pamEnd: Math.min(idx + 23, cds.length),
        isSense: true,
        matchSeq: proto,
      };
    }

    // 2. Reverse complement search in CDS (for minus strand guides)
    const rcProto = reverseComplement(proto);
    idx = cds.indexOf(rcProto);
    if (idx !== -1) {
      const pamStart = Math.max(0, idx - 3);
      return {
        protoStart: idx,
        protoEnd: idx + 20,
        pamStart,
        pamEnd: idx,
        isSense: false,
        matchSeq: rcProto,
      };
    }

    // 3. 15-nt seed search (PAM-proximal seed)
    const seed15 = proto.slice(5);
    idx = cds.indexOf(seed15);
    if (idx !== -1) {
      const pStart = Math.max(0, idx - 5);
      return {
        protoStart: pStart,
        protoEnd: pStart + 20,
        pamStart: pStart + 20,
        pamEnd: Math.min(pStart + 23, cds.length),
        isSense: true,
        matchSeq: cds.slice(pStart, pStart + 20),
      };
    }

    const rcSeed15 = reverseComplement(seed15);
    idx = cds.indexOf(rcSeed15);
    if (idx !== -1) {
      const pStart = idx;
      return {
        protoStart: pStart,
        protoEnd: pStart + 20,
        pamStart: Math.max(0, pStart - 3),
        pamEnd: pStart,
        isSense: false,
        matchSeq: cds.slice(pStart, pStart + 20),
      };
    }

    return {
      protoStart: 0,
      protoEnd: Math.min(20, cds.length),
      pamStart: Math.min(20, cds.length),
      pamEnd: Math.min(23, cds.length),
      isSense: true,
      matchSeq: proto,
    };
  }, [cdsDisplay, currentGuide.protospacer_sequence, currentGuide.pam_sequence]);

  // ── Synchronized 3D sequence: 20-nt protospacer (0..19) + 3-nt PAM (20..22) + 7-nt flank (23..29)
  const displaySequence = useMemo(() => {
    if (currentGuide.protospacer_sequence) {
      const proto = currentGuide.protospacer_sequence.padEnd(20, 'A').slice(0, 20);
      const pam = (currentGuide.pam_sequence || 'TGG').padEnd(3, 'G').slice(0, 3);
      let flank = 'AAGAAAT';
      if (currentGuide.context_30nt_sequence && currentGuide.context_30nt_sequence.length >= 30) {
        flank = currentGuide.context_30nt_sequence.slice(23, 30).padEnd(7, 'A');
      }
      return `${proto}${pam}${flank}`.slice(0, 30);
    }
    return 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA';
  }, [currentGuide]);

  // Auto-scroll sequence container when scanning or when stage changes
  useEffect(() => {
    if (!seqContainerRef.current || !cdsDisplay) return;
    const container = seqContainerRef.current;
    const scrollMax = container.scrollWidth - container.clientWidth;
    if (scrollMax <= 0) return;

    if (isScanning) {
      container.scrollLeft = scrollMax * scanProgress;
    } else if (simStageIndex >= 1 && targetCoords.protoStart >= 0) {
      const targetRatio = targetCoords.protoStart / Math.max(1, cdsDisplay.length);
      const targetPos = targetRatio * container.scrollWidth - container.clientWidth / 2 + 100;
      container.scrollTo({
        left: Math.max(0, Math.min(scrollMax, targetPos)),
        behavior: 'smooth',
      });
    }
  }, [isScanning, scanProgress, simStageIndex, cdsDisplay, targetCoords]);

  // ── Animation Loop ──────────────────────────────────────────────────────────
  const runAnimationFrame = useCallback((timestamp: number) => {
    if (!isPlaying) return;

    const stageDuration = SIM_STAGES[simStageIndex]?.durationMs || 0;
    if (stageDuration === 0) return;

    const elapsed = timestamp - stageStartTimeRef.current;
    const t = Math.min(elapsed / stageDuration, 1);

    if (simStageIndex === 0) {
      // Stage 01: DNA Scanning
      progressRef.current.scan = t;
      setScanProgress(t);
    } else if (simStageIndex === 3) {
      // Stage 04: Guide RNA Binding
      progressRef.current.approach = t;
      setApproachProgress(t);
    }

    if (t < 1) {
      animFrameRef.current = requestAnimationFrame(runAnimationFrame);
    } else {
      // Advance to next stage
      const nextIdx = simStageIndex + 1;
      if (nextIdx < SIM_STAGES.length) {
        stageStartTimeRef.current = performance.now();
        setSimStageIndex(nextIdx);
        setScanProgress(0);
        setApproachProgress(0);
        animFrameRef.current = requestAnimationFrame(runAnimationFrame);
      } else {
        // Stage 06 Predicted Cleavage completed!
        setIsPlaying(false);
        setSimCompleted(true);
        // Automatically navigate to TOPSIS Ranking after simulation completion
        setNavigatingToTOPSIS(true);
        setTimeout(() => {
          navigate('/topsis-ranking');
        }, 2200);
      }
    }
  }, [isPlaying, simStageIndex, navigate]);

  useEffect(() => {
    if (isPlaying && simStageIndex >= 0) {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      stageStartTimeRef.current = performance.now();
      animFrameRef.current = requestAnimationFrame(runAnimationFrame);
    }
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isPlaying, simStageIndex, runAnimationFrame]);

  // ── Simulation Controls ─────────────────────────────────────────────────────
  const handlePlay = () => {
    if (simCompleted) return;
    if (simStageIndex === -1) {
      setScanProgress(0);
      setApproachProgress(0);
      setSimCompleted(false);
      setSimStageIndex(0);
    }
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
  };

  const handleRestart = () => {
    setIsPlaying(false);
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    setSimStageIndex(-1);
    setScanProgress(0);
    setApproachProgress(0);
    setSimCompleted(false);
    setNavigatingToTOPSIS(false);
  };

  const handleSkipStage = () => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    const nextIdx = simStageIndex + 1;
    setScanProgress(0);
    setApproachProgress(0);
    if (nextIdx < SIM_STAGES.length) {
      stageStartTimeRef.current = performance.now();
      setSimStageIndex(nextIdx);
      if (isPlaying) {
        animFrameRef.current = requestAnimationFrame(runAnimationFrame);
      }
    } else {
      setIsPlaying(false);
      setSimCompleted(true);
    }
  };

  // Auto-start simulation when navigated here with autoStart flag
  useEffect(() => {
    if (stateData?.autoStart && simStageIndex === -1 && !loadingGuides) {
      const timer = setTimeout(() => {
        setScanProgress(0);
        setApproachProgress(0);
        setSimCompleted(false);
        setSimStageIndex(0);
        setIsPlaying(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadingGuides]);

  const stageColors: Record<string, string> = {
    cyan: 'border-cyan-500/60 bg-cyan-500/10 text-cyan-300',
    amber: 'border-amber-500/60 bg-amber-500/10 text-amber-300',
    emerald: 'border-emerald-500/60 bg-emerald-500/10 text-emerald-300',
    indigo: 'border-indigo-500/60 bg-indigo-500/10 text-indigo-300',
    violet: 'border-violet-500/60 bg-violet-500/10 text-violet-300',
    red: 'border-red-500/60 bg-red-500/10 text-red-300',
  };

  // If user visits Design Studio directly with no analysis run and no selection
  const hasActiveAnalysis = !!stateData?.geneSymbol || !!latestAnalysis || candidateGuides.length > 0;

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.5} />

      {/* ── Page Header ──────────────────────────────────────────────────── */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Computational Simulation &bull; 3D Molecular Viewer
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Boxes className="w-7 h-7 text-cyan-400" />
              <span>3D CRISPR Design Studio</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Live computational simulation of DNA scanning, PAM detection, target protospacer recognition, guide RNA binding, SpCas9 complex formation, and predicted cleavage site mapping.
            </p>
          </div>

          {/* Simulation Play Controls */}
          <div className="flex items-center gap-2">
            {!isPlaying ? (
              <button
                onClick={handlePlay}
                disabled={simCompleted}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
              >
                <Play size={13} fill="currentColor" />
                <span>{simStageIndex === -1 ? 'Start 3D Simulation' : 'Resume'}</span>
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
              >
                <Pause size={13} fill="currentColor" />
                <span>Pause</span>
              </button>
            )}

            <button
              onClick={handleSkipStage}
              disabled={simStageIndex === -1 || simCompleted}
              className="p-2.5 rounded-lg text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-700 border border-slate-700/60 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              title="Skip to Next Stage"
            >
              <SkipForward size={14} />
            </button>
            <button
              onClick={handleRestart}
              className="p-2.5 rounded-lg text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-700 border border-slate-700/60 transition-colors cursor-pointer"
              title="Restart Simulation"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        </div>
      </div>

      {!hasActiveAnalysis && (
        <div className="research-card p-12 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-xl space-y-4">
          <Dna className="w-12 h-12 text-slate-600 mx-auto opacity-50" />
          <div className="text-base font-bold text-slate-300">No active analysis selected.</div>
          <div className="text-slate-400 max-w-md mx-auto leading-relaxed">
            Select a target cancer entity and oncogene to initialize the 3D computational simulation with verified GENCODE v46 sequence data.
          </div>
          <button
            onClick={() => navigate('/analysis-pipeline')}
            className="mt-2 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
          >
            <span>Start New Analysis</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* ── Post-Simulation Notice & Automatic Navigation Banner ─────────────── */}
      {simCompleted && (
        <div className="research-card p-4 border-emerald-500/40 bg-gradient-to-r from-emerald-950/60 via-slate-900/70 to-slate-950/90 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-7 h-7 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-bold text-emerald-300">
                Simulation Completed &bull; Primary Guide: {currentGuide.protospacer_sequence} ({currentGuide.pam_sequence})
              </p>
              <p className="text-xs text-slate-400">
                {navigatingToTOPSIS
                  ? 'Navigating to TOPSIS Multi-Criteria Decision Ranking...'
                  : 'Predicted Cleavage Site: −3 bp upstream of PAM on sense strand. Ready for TOPSIS ranking.'}
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/topsis-ranking')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20 transition-all cursor-pointer flex-shrink-0"
          >
            <Award size={14} />
            <span>Proceed to TOPSIS Ranking</span>
            <ChevronRight size={14} />
          </button>
        </div>
      )}

      {/* ── Main Grid ────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left/Center — 3D Canvas + Stage Bar */}
        <div className="lg:col-span-8 space-y-4">

          {/* 6 Stage Progress Bar */}
          <div className="research-card p-3 border-slate-800">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
              {SIM_STAGES.map((st, idx) => {
                const isActive = simStageIndex === idx;
                const isDone = simStageIndex > idx;
                const Icon = st.icon;
                const colCls = isDone
                  ? 'border-slate-700 bg-slate-800/60 text-slate-400'
                  : isActive
                  ? stageColors[st.color] || 'border-cyan-500/60 bg-cyan-500/10 text-cyan-300'
                  : 'border-slate-800 bg-slate-900/40 text-slate-600';
                return (
                  <div key={st.id} className="flex items-center gap-1 min-w-0">
                    <div
                      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-[10px] font-bold font-mono uppercase whitespace-nowrap transition-all ${colCls}`}
                    >
                      {isDone ? (
                        <CheckCircle size={10} className="text-slate-400" />
                      ) : (
                        <Icon size={10} />
                      )}
                      <span>{st.numStr} {st.label}</span>
                    </div>
                    {idx < SIM_STAGES.length - 1 && (
                      <ChevronRight size={12} className={isDone || isActive ? 'text-slate-500' : 'text-slate-700'} />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Current stage description + progress bar */}
            {currentStage && (
              <div className="mt-2.5 space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-200 font-bold font-mono">Stage {currentStage.numStr}: {currentStage.label}</span>
                  {currentStage.id === 'COMPLETED' && (
                    <span className="text-[10px] font-mono text-red-400 font-bold bg-red-950/60 px-2 py-0.5 rounded border border-red-800/40">
                      Predicted Cleavage Site
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{currentStage.description}</p>
                {currentStage.durationMs > 0 && (
                  <div className="w-full h-1 rounded-full bg-slate-800 overflow-hidden mt-1">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-150"
                      style={{
                        width: `${Math.round(
                          (simStageIndex === 0 ? scanProgress : simStageIndex === 3 ? approachProgress : 0.6) * 100
                        )}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 3D Canvas */}
          <div className="research-card border-slate-800 bg-slate-950 relative" style={{ height: '480px' }}>
            <div className="absolute inset-0 rounded-xl overflow-hidden">
              <DNAScene
                stage={activeStage}
                sequence={displaySequence}
                guideSequence={currentGuide.protospacer_sequence}
                isScanning={isScanning}
                highlightPam={highlightPam}
                highlightGuide={highlightGuide}
                cas9Visible={cas9Visible}
                cleavageActive={cleavageActive}
                scanProgress={scanProgress}
                approachProgress={approachProgress}
                targetY={-1.76}
              />
            </div>

            {/* Canvas overlay: guide info */}
            <div className="absolute top-3 left-3 z-10 flex items-center gap-2 pointer-events-none">
              <span className="text-[10px] font-mono font-bold text-cyan-400 bg-slate-950/90 px-2 py-1 rounded border border-cyan-800/40">
                {selectedGeneSymbol} &bull; Guide RNA {selectedGuideIndex + 1}: {currentGuide.protospacer_sequence} ({currentGuide.pam_sequence})
              </span>
              {isPlaying && (
                <span className="text-[10px] font-mono font-bold text-amber-300 bg-slate-950/90 px-2 py-1 rounded border border-amber-700/40 animate-pulse">
                  ● SIMULATING
                </span>
              )}
              {simCompleted && (
                <span className="text-[10px] font-mono font-bold text-emerald-300 bg-slate-950/90 px-2 py-1 rounded border border-emerald-700/40">
                  ✓ PREDICTED CLEAVAGE SITE
                </span>
              )}
            </div>

            <div className="absolute bottom-3 right-3 z-10 pointer-events-none text-[10px] font-mono text-slate-500">
              Drag to Rotate &bull; Scroll to Zoom
            </div>
          </div>

          {/* Live Target Gene CDS Sequence Scanner (Requirements 10-15) */}
          {cdsDisplay && (
            <div className="research-card p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <SectionHeader
                  title="Target DNA / CDS Sequence Scanning"
                  subtitle={`${selectedGeneSymbol} Coding Sequence — ${cdsDisplay.length.toLocaleString()} bp (GRCh38 / GENCODE v46)`}
                />
                {isScanning && (
                  <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-700/60 animate-pulse flex items-center gap-1.5 w-fit">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                    <span>Live Scanning Window: 5&apos;-NGG PAM Search ({Math.round(scanProgress * 100)}%)</span>
                  </span>
                )}
                {!isScanning && simStageIndex === 1 && (
                  <span className="text-[10px] font-mono text-amber-300 bg-amber-950/80 px-2.5 py-1 rounded border border-amber-700/60 flex items-center gap-1.5 w-fit animate-pulse">
                    <Target size={11} className="text-amber-400" />
                    <span>PAM Detected: {currentGuide.pam_sequence} at locus {targetCoords.pamStart + 1}</span>
                  </span>
                )}
                {!isScanning && simStageIndex >= 2 && (
                  <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-700/60 flex items-center gap-1.5 w-fit">
                    <CheckCircle size={11} className="text-cyan-400" />
                    <span>Target Recognized: Locus {targetCoords.protoStart + 1}–{targetCoords.protoEnd} ({currentGuide.strand} Strand)</span>
                  </span>
                )}
              </div>

              {/* Real Sequence Scrolling Window */}
              <div
                ref={seqContainerRef}
                className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs overflow-x-auto select-none"
                style={{ scrollBehavior: isScanning ? 'auto' : 'smooth' }}
              >
                <div className="flex items-center gap-2 pb-2">
                  <span className="text-slate-500 shrink-0 text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                    5&apos; SENSE
                  </span>
                  
                  {/* Single-line continuous nucleotide track */}
                  <div className="flex flex-nowrap items-center gap-[1px] tracking-wider whitespace-nowrap">
                    {cdsDisplay.split('').map((base, idx) => {
                      const scanWindowStart = isScanning
                        ? Math.floor(scanProgress * Math.max(1, cdsDisplay.length - 23))
                        : -1;
                      const isInScanWindow = isScanning && idx >= scanWindowStart && idx < scanWindowStart + 23;

                      const inProtospacer = simStageIndex >= 2 && targetCoords.protoStart >= 0 && idx >= targetCoords.protoStart && idx < targetCoords.protoEnd;
                      const inPam = simStageIndex >= 1 && targetCoords.pamStart >= 0 && idx >= targetCoords.pamStart && idx < targetCoords.pamEnd;
                      const isCleavageCut = simStageIndex >= 5 && targetCoords.protoStart >= 0 && (targetCoords.isSense ? idx === targetCoords.protoEnd - 3 : idx === targetCoords.protoStart + 3);

                      let cls = 'inline-block text-center w-4 h-6 leading-6 text-xs transition-colors rounded-sm';
                      if (isInScanWindow) {
                        cls = 'inline-block text-center w-4 h-6 leading-6 text-xs bg-cyan-500/50 text-cyan-100 font-bold border-b-2 border-cyan-400 shadow-md shadow-cyan-500/30';
                      } else if (isCleavageCut) {
                        cls = 'inline-block text-center w-4 h-6 leading-6 text-xs bg-red-500/60 text-white font-extrabold border border-red-400 animate-pulse';
                      } else if (inProtospacer) {
                        cls = 'inline-block text-center w-4 h-6 leading-6 text-xs bg-cyan-500/30 text-cyan-200 font-bold border-t border-b border-cyan-400/80';
                      } else if (inPam) {
                        cls = 'inline-block text-center w-4 h-6 leading-6 text-xs bg-amber-500/40 text-amber-200 font-extrabold border border-amber-400 shadow-sm shadow-amber-500/40';
                      } else {
                        if (base === 'A') cls += ' text-emerald-400/80 hover:bg-slate-900';
                        else if (base === 'T') cls += ' text-red-400/80 hover:bg-slate-900';
                        else if (base === 'G') cls += ' text-blue-400/80 hover:bg-slate-900';
                        else if (base === 'C') cls += ' text-amber-300/80 hover:bg-slate-900';
                        else cls += ' text-slate-400';
                      }

                      return (
                        <span
                          key={idx}
                          className={cls}
                          title={`Position ${idx + 1}: ${base}${inProtospacer ? ' (Protospacer)' : ''}${inPam ? ' (PAM)' : ''}`}
                        >
                          {base}
                        </span>
                      );
                    })}
                  </div>

                  <span className="text-slate-500 shrink-0 text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                    3&apos;
                  </span>
                </div>

                {/* Scan coordinate indicator */}
                <div className="flex items-center justify-between gap-3 text-[10px] text-slate-400 pt-2 border-t border-slate-800/80 flex-wrap">
                  <div className="flex items-center gap-3 flex-wrap font-mono">
                    <span>CDS Length: <strong className="text-slate-200">{cdsDisplay.length.toLocaleString()} bp</strong></span>
                    <span>&bull;</span>
                    <span>GC Content: <strong className="text-slate-200">{((cdsDisplay.split('').filter(b => b === 'G' || b === 'C').length / cdsDisplay.length) * 100).toFixed(1)}%</strong></span>
                    <span>&bull;</span>
                    <span>
                      Target Locus: <strong className="text-cyan-400">
                        {targetCoords.protoStart >= 0 ? `bp ${targetCoords.protoStart + 1}–${targetCoords.protoEnd}` : 'Pending Detection'}
                      </strong>
                    </span>
                    <span>&bull;</span>
                    <span>
                      PAM Locus: <strong className="text-amber-400">
                        {targetCoords.pamStart >= 0 ? `bp ${targetCoords.pamStart + 1}–${targetCoords.pamEnd} (${currentGuide.pam_sequence})` : 'Pending'}
                      </strong>
                    </span>
                  </div>
                  {isScanning && (
                    <span className="text-cyan-400 font-bold font-mono animate-pulse">
                      Scanning: {Math.round(scanProgress * 100)}% (Locus ~{Math.floor(scanProgress * cdsDisplay.length)} bp)
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Target DNA Sequence + PAM + Protospacer + Predicted Cleavage Site */}
          <div className="research-card p-5 space-y-3">
            <SectionHeader
              title="Target Sequence Mapping &amp; Predicted Cleavage Locus"
              subtitle={`Sense strand mapping for ${selectedGeneSymbol} (GRCh38)`}
            />

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs space-y-3 overflow-x-auto">
              {/* Sense strand */}
              <div className="flex items-start gap-2">
                <span className="text-slate-500 shrink-0 pt-0.5">5&apos; &rarr; 3&apos;</span>
                <span className="tracking-wider flex flex-wrap gap-0.5 items-center">
                  <span className="text-slate-500">···</span>
                  <span className="bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded font-bold border border-cyan-500/30 flex items-center gap-1">
                    <span>{currentGuide.protospacer_sequence.slice(0, 17)}</span>
                    <span className="text-red-400 font-extrabold text-sm" title="Predicted Cleavage Site (−3 bp upstream of PAM)">╎</span>
                    <span className="text-cyan-200 font-bold">{currentGuide.protospacer_sequence.slice(17)}</span>
                  </span>
                  <span className="bg-amber-500/20 text-amber-300 px-2 py-1 rounded font-bold border border-amber-500/30">
                    {currentGuide.pam_sequence}
                  </span>
                  <span className="text-slate-500">···</span>
                </span>
              </div>

              {/* Cleavage indicator */}
              <div className="flex items-center gap-3 text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 flex-wrap">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400 shrink-0" />
                  <span>Target Protospacer (20-nt)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-amber-400 shrink-0" />
                  <span>SpCas9 PAM (5&apos;-NGG)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-red-400 shrink-0" />
                  <span>
                    Predicted Cleavage Site:{' '}
                    {currentGuide.cleavage_coordinate
                      ? `chr${selectedGene?.chromosome || '17'}:${currentGuide.cleavage_coordinate.toLocaleString()} (GRCh38 −3 bp from PAM)`
                      : '−3 bp upstream of PAM'}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 italic">
              Computational simulation only. Predicted binding and cleavage loci are not experimental gene editing results.
            </p>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="lg:col-span-4 space-y-4">

          {/* Target Gene Selector */}
          <div className="research-card p-5 space-y-4">
            <SectionHeader
              title="Target Gene"
              subtitle="Validated cancer target gene"
            />
            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                  Cancer Type
                </label>
                <select
                  value={selectedCancer}
                  onChange={(e) => {
                    const newCancer = e.target.value;
                    setSelectedCancer(newCancer);
                    const geneList = CANCER_GENE_MAP[newCancer] || [];
                    if (geneList.length > 0) setSelectedGeneSymbol(geneList[0]);
                    handleRestart();
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Breast cancer">Breast Cancer</option>
                  <option value="Lung cancer">Lung Cancer</option>
                  <option value="Liver cancer">Liver Cancer</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                  Target Gene
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(CANCER_GENE_MAP[selectedCancer] || []).map((sym) => (
                    <button
                      key={sym}
                      onClick={() => { setSelectedGeneSymbol(sym); handleRestart(); }}
                      className={`px-3 py-2 rounded-lg text-xs font-bold font-mono transition-all cursor-pointer ${
                        selectedGeneSymbol === sym
                          ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                          : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800'
                      }`}
                    >
                      {sym}
                    </button>
                  ))}
                </div>
                {selectedGeneSymbol && (
                  <p className="text-[10px] text-slate-400 mt-1.5 font-mono">
                    {GENE_FULL_NAMES[selectedGeneSymbol] || selectedGeneSymbol}
                  </p>
                )}
              </div>
            </div>

            {selectedGene && (
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">NCBI Gene ID:</span>
                  <span className="font-mono text-slate-200">{selectedGene.ncbi_gene_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Ensembl ID:</span>
                  <span className="font-mono text-slate-200 text-[10px]">{selectedGene.ensembl_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Chromosome:</span>
                  <span className="font-mono text-slate-200">Chr {selectedGene.chromosome} ({selectedGene.strand})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Canonical Transcript:</span>
                  <span className="font-mono text-slate-200 text-[10px]">{selectedGene.canonical_transcript_id}</span>
                </div>
              </div>
            )}
          </div>

          {/* Candidate Guide RNAs Selector */}
          <div className="research-card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <SectionHeader
                title="Candidate Guide RNAs"
                subtitle={`SpCas9 guides identified for ${selectedGeneSymbol}`}
              />
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                GENCODE v46
              </span>
            </div>

            {loadingGuides ? (
              <div className="text-center py-8 text-xs font-mono text-slate-400">
                Extracting candidate guides from GRCh38 CDS...
              </div>
            ) : candidateGuides.length === 0 ? (
              <div className="text-center py-8 text-xs font-mono text-slate-500">
                No candidates available. Start an analysis run.
              </div>
            ) : (
              <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                {candidateGuides.map((g, idx) => (
                  <div
                    key={g.id || idx}
                    onClick={() => { setSelectedGuideIndex(idx); handleRestart(); }}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      selectedGuideIndex === idx
                        ? 'bg-slate-900/90 border-cyan-500/60 shadow-sm shadow-cyan-500/10'
                        : 'bg-slate-900/30 border-slate-800/80 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-white font-mono">Guide RNA {idx + 1}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/40 font-bold flex items-center gap-1">
                        <Sparkles size={9} />
                        {g.exon_number ? `Exon ${g.exon_number}` : 'CDS'}
                      </span>
                    </div>
                    <div className="text-xs font-mono text-cyan-300 tracking-wider">
                      {g.protospacer_sequence}{' '}
                      <span className="text-amber-400 font-bold">{g.pam_sequence}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1 mt-1.5 text-[10px] text-slate-400 font-mono">
                      <div>GC: {g.gc_percentage.toFixed(1)}%</div>
                      <div>Strand: {g.strand}</div>
                      <div>{g.genomic_start.toLocaleString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 3D Scene Key */}
          <div className="research-card p-4 space-y-2">
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">3D Scene Structure Key</p>
            <div className="space-y-1.5 text-[11px] text-slate-400">
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#22d3ee] shrink-0" /><span>5&apos; Sugar-Phosphate Backbone (Strand 1)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#818cf8] shrink-0" /><span>3&apos; Sugar-Phosphate Backbone (Strand 2)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#22c55e] shrink-0" /><span>Adenine (A)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#ef4444] shrink-0" /><span>Thymine (T)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#3b82f6] shrink-0" /><span>Guanine (G)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#eab308] shrink-0" /><span>Cytosine (C)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#f97316] shrink-0" /><span>SpCas9 NGG PAM</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#f43f5e] shrink-0" /><span>Guide RNA (single-stranded)</span></div>
              <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#ef4444] shrink-0 animate-pulse" /><span>Predicted Cleavage Site</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Workflow Navigation Footer (Requirement 22) ─────────────────── */}
      <WorkflowNavigationFooter
        prevPath="/analysis-pipeline"
        prevLabel="← Analysis Pipeline"
        nextPath="/topsis-ranking"
        nextLabel="Next: TOPSIS Ranking →"
      />
    </div>
  );
};
