import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { DNAHelix } from './DNAHelix';
import { SequenceScanner } from './SequenceScanner';
import { GRNABinding } from './GRNABinding';
import { Cas9Complex } from './Cas9Complex';
import { CleavageSite } from './CleavageSite';
import { OffTargetGenome } from './OffTargetGenome';
import { MLDataFlow } from './MLDataFlow';
import { TOPSISSpace } from './TOPSISSpace';
import { PipelineStage } from '../../types';

export interface DNASceneProps {
  stage?: PipelineStage;
  sequence?: string;
  guideSequence?: string;
  isScanning?: boolean;
  highlightPam?: boolean;
  highlightGuide?: boolean;
  cas9Visible?: boolean;
  cleavageActive?: boolean;
  scannerPos?: number;
  previewOnly?: boolean;
  /** 0-1 scanning travel progress */
  scanProgress?: number;
  /** 0-1 RNA approach/docking progress */
  approachProgress?: number;
  /** Y center of the target protospacer on the helix */
  targetY?: number;
}

export const DNAScene: React.FC<DNASceneProps> = ({
  stage = 'IDLE',
  sequence = 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
  guideSequence = 'GCAGCCAGATGCCTGGACAG',
  isScanning = false,
  highlightPam = false,
  highlightGuide = false,
  cas9Visible = false,
  cleavageActive = false,
  scannerPos = -1,
  previewOnly = false,
  scanProgress = 0,
  approachProgress = 0,
  targetY = 0,
}) => {
  const showHelix = true;
  const showScanner = (stage === 'GRNA_IDENTIFICATION' || isScanning) && !previewOnly;
  const showBinding = (
    stage === 'GRNA_IDENTIFICATION' ||
    stage === 'ON_TARGET' ||
    stage === 'OFF_TARGET' ||
    stage === 'COMPLETED' ||
    highlightGuide
  ) && !previewOnly;
  const showCas9 = (stage === 'COMPLETED' || cas9Visible) && !previewOnly;
  const showCleavage = (stage === 'COMPLETED' || cleavageActive) && !previewOnly;
  const showOffTarget = stage === 'OFF_TARGET' && !previewOnly;
  const showML = stage === 'ON_TARGET' && !previewOnly;
  const showTOPSIS = stage === 'RANKING' && !previewOnly;

  return (
    <div
      className="three-canvas w-full h-full relative"
      style={{ minHeight: previewOnly ? '220px' : '460px' }}
    >
      <Canvas
        camera={{ position: previewOnly ? [0, 0, 7.5] : [0, 1.5, 9.5], fov: 44 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.35} />
        <pointLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[-10, -10, -10]} color="#0ea5e9" intensity={0.5} />
        <directionalLight position={[0, 6, 5]} intensity={0.9} />

        <Suspense fallback={null}>
          <Stars
            radius={55}
            depth={50}
            count={previewOnly ? 500 : 1400}
            factor={4}
            saturation={0}
            fade
            speed={0.8}
          />

          {/* DNA Double Helix — always visible throughout all stages */}
          {showHelix && (
            <DNAHelix
              sequence={sequence}
              highlightPam={highlightPam || stage === 'COMPLETED'}
              highlightGuide={highlightGuide || stage === 'COMPLETED'}
              scannerPos={scannerPos}
              cleavageActive={showCleavage}
              rotationSpeed={previewOnly ? 0.18 : (isScanning ? 0.15 : 0.25)}
            />
          )}

          {/* Scanning ring sweeping along the helix */}
          <SequenceScanner
            active={showScanner}
            totalLength={sequence.length}
            scanProgress={showScanner ? scanProgress : undefined}
          />

          {/* Guide RNA strand — scans then docks on protospacer */}
          <GRNABinding
            active={showBinding}
            isScanning={showScanner}
            guideSequence={guideSequence}
            scanProgress={scanProgress}
            approachProgress={approachProgress}
            targetY={targetY}
          />

          {/* SpCas9 Protein Complex */}
          <Cas9Complex visible={showCas9} />

          {/* Predicted Cleavage Site indicator */}
          <CleavageSite active={showCleavage} />

          {/* Off-target genome visualization */}
          <OffTargetGenome visible={showOffTarget} />

          {/* Machine-learning data flow */}
          <MLDataFlow visible={showML} />

          {/* TOPSIS decision space */}
          <TOPSISSpace visible={showTOPSIS} />
        </Suspense>

        <OrbitControls
          enablePan={!previewOnly}
          enableZoom={!previewOnly}
          enableRotate
          autoRotate={previewOnly}
          autoRotateSpeed={0.7}
          maxDistance={20}
          minDistance={3}
        />
      </Canvas>

      {/* Scientific disclaimer watermark */}
      <div className="absolute bottom-2 left-3 pointer-events-none text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800 backdrop-blur flex items-center gap-2">
        <span className="text-cyan-400 font-bold">Computational Simulation</span>
        <span className="text-slate-600">&bull;</span>
        <span>Guide RNA directs SpCas9 toward complementary target DNA adjacent to PAM</span>
        <span className="text-slate-600">&bull;</span>
        <span className="text-red-400 font-semibold">Predicted Cleavage Site</span>
      </div>
    </div>
  );
};
