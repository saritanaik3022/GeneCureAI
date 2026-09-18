import React, { useState, useEffect } from 'react';
import { Filter, Dna, Database, Layers, CheckCircle2 } from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { ModeBadge } from '../components/common/ModeBadge';
import { StatusBadge } from '../components/common/StatusBadge';

import { useHealth } from '../hooks/useHealth';
import { scanGuides } from '../services/api';
import { GuideRNA, GuideDesignScanResponse } from '../types';
import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';

export const GRNACandidatesPage: React.FC = () => {
  const { health } = useHealth();
  const [selectedGene, setSelectedGene] = useState('BRCA1');
  const [candidates, setCandidates] = useState<GuideRNA[]>([]);
  const [metadata, setMetadata] = useState<GuideDesignScanResponse | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gcFilter, setGcFilter] = useState<number>(0);

  useEffect(() => {
    setLoading(true);
    setError(null);
    scanGuides({ gene_symbol: selectedGene })
      .then((res) => {
        setCandidates(res.candidates);
        setMetadata(res.metadata);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Scan failed', err);
        setError(err.message || 'Failed to scan candidate guides');
        setLoading(false);
      });
  }, [selectedGene]);

  const filteredCandidates = candidates.filter((c) => c.gc_percentage >= gcFilter);

  return (
    <div className="relative w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 fade-in">
      <ScientificMolecularBackground intensity={0.55} />
      {/* Header */}
      <div className="research-card p-6 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950/90">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                Stage 02 &bull; Discovery &amp; Extraction
              </span>
              <ModeBadge mode={health?.execution_mode || 'REAL_MODE'} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Dna className="w-7 h-7 text-cyan-400" />
              <span>Candidate gRNA Identification Table</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Dual-strand in-silico discovery of 20-nt candidate guide RNAs targeting SpCas9 5&apos;-NGG PAM motifs across exonic coding sequences (CDS).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedGene}
              onChange={(e) => setSelectedGene(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-cyan-400 font-bold focus:outline-none focus:border-cyan-500"
            >
              {['BRCA1', 'HER2', 'TP53', 'EGFR', 'KRAS', 'ALK', 'CTNNB1', 'AXIN1', 'TERT'].map((g) => (
                <option key={g} value={g}>
                  Target: {g}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>



      {/* Real Genomic Provenance Bar (when metadata available) */}
      {metadata && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="research-card p-3 border-cyan-900/40 bg-cyan-950/20">
            <div className="text-[10px] text-cyan-400 font-mono font-bold uppercase flex items-center gap-1">
              <Database size={11} /> Assembly &amp; GTF
            </div>
            <div className="text-xs font-mono font-extrabold text-white mt-1">
              {metadata.genome} / {metadata.annotation}
            </div>
          </div>
          <div className="research-card p-3 border-slate-800">
            <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Locus &amp; Strand</div>
            <div className="text-xs font-mono font-extrabold text-white mt-1">
              {metadata.chromosome} ({metadata.strand})
            </div>
          </div>
          <div className="research-card p-3 border-slate-800">
            <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">Transcript</div>
            <div className="text-xs font-mono font-extrabold text-cyan-400 mt-1 truncate" title={metadata.transcript}>
              {metadata.transcript}
            </div>
          </div>
          <div className="research-card p-3 border-slate-800">
            <div className="text-[10px] text-slate-400 font-mono font-bold uppercase flex items-center gap-1">
              <Layers size={11} /> Exons Scanned
            </div>
            <div className="text-xs font-mono font-extrabold text-white mt-1">
              {metadata.total_exons_scanned} CDS Exons
            </div>
          </div>
          <div className="research-card p-3 border-slate-800">
            <div className="text-[10px] text-slate-400 font-mono font-bold uppercase">CDS Length</div>
            <div className="text-xs font-mono font-extrabold text-white mt-1">
              {metadata.cds_length_scanned.toLocaleString()} bp
            </div>
          </div>
          <div className="research-card p-3 border-slate-800">
            <div className="text-[10px] text-slate-400 font-mono font-bold uppercase flex items-center gap-1">
              <CheckCircle2 size={11} className="text-emerald-400" /> Guides Found
            </div>
            <div className="text-xs font-mono font-extrabold text-emerald-400 mt-1">
              {metadata.candidate_count} Candidates
            </div>
          </div>
        </div>
      )}

      {/* Filter / Controls */}
      <div className="research-card p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-slate-400" />
            <span className="text-xs font-semibold text-slate-300">Min GC Content:</span>
            <span className="text-xs font-mono text-cyan-400 font-bold">{gcFilter}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="70"
            step="5"
            value={gcFilter}
            onChange={(e) => setGcFilter(Number(e.target.value))}
            className="w-32 accent-cyan-400 cursor-pointer"
          />
        </div>

        <div className="text-xs text-slate-400">
          Showing <strong className="text-white font-mono">{filteredCandidates.length}</strong> candidate guides for <strong className="text-cyan-400">{selectedGene}</strong>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs font-mono">
          {error}
        </div>
      )}

      {/* Main Candidate Table */}
      <div className="research-card p-5">
        <SectionHeader
          title="Candidate Guide RNAs"
          subtitle="Identified SpCas9 protospacers with biophysical sequence properties"
        />

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs font-mono">
            Scanning CDS for 5&apos;-NGG PAM motifs across GENCODE v46 exonic coordinates...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Candidate ID</th>
                  <th>Protospacer Sequence (5&apos; &rarr; 3&apos;)</th>
                  <th>PAM</th>
                  <th>Strand</th>
                  <th>Exon</th>
                  <th>Genomic Coordinates (GRCh38)</th>
                  <th>Cleavage Pos</th>
                  <th>GC %</th>
                  <th>Poly-T Terminator</th>
                  <th>Self-Comp.</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredCandidates.map((c, idx) => (
                  <tr key={c.id}>
                    <td className="font-mono text-cyan-400 font-semibold">Guide RNA {idx + 1}</td>
                    <td className="font-mono text-white font-bold tracking-wider">{c.protospacer_sequence}</td>
                    <td className="font-mono text-amber-400 font-extrabold">{c.pam_sequence}</td>
                    <td className="font-mono font-bold">{c.strand}</td>
                    <td className="font-mono text-slate-300">{c.exon_number ? `Exon ${c.exon_number}` : '--'}</td>
                    <td className="font-mono text-[11px] text-slate-400">
                      {c.chromosome ? `${c.chromosome}:` : ''}{c.genomic_start.toLocaleString()} - {c.genomic_end.toLocaleString()}
                    </td>
                    <td className="font-mono text-[11px] text-cyan-300">
                      {c.cleavage_coordinate ? c.cleavage_coordinate.toLocaleString() : '--'}
                    </td>
                    <td className="font-mono font-semibold text-slate-200">{c.gc_percentage.toFixed(1)}%</td>
                    <td>
                      {c.has_poly_t_terminator ? (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
                          DETECTED
                        </span>
                      ) : (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400">
                          NONE
                        </span>
                      )}
                    </td>
                    <td className="font-mono text-slate-300">{c.self_complementarity_score.toFixed(2)}</td>
                    <td>
                      <StatusBadge status="Candidate gRNA" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
