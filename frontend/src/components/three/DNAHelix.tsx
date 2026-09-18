import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface DNAHelixProps {
  sequence?: string;
  highlightPam?: boolean;
  highlightGuide?: boolean;
  scannerPos?: number;
  cleavageActive?: boolean;
  rotationSpeed?: number;
}

// Nucleotide base colors for scientific fidelity
const NUC_COLORS: Record<string, string> = {
  A: '#22c55e', // Green (Adenine)
  T: '#ef4444', // Red (Thymine)
  G: '#3b82f6', // Blue (Guanine)
  C: '#eab308', // Yellow (Cytosine)
};

const COMPLEMENT: Record<string, string> = {
  A: 'T',
  T: 'A',
  G: 'C',
  C: 'G',
};

export const DNAHelix: React.FC<DNAHelixProps> = ({
  sequence = 'ATGGATTTATCTGCTCTTCGCGTTGAAGAA',
  highlightPam = false,
  highlightGuide = false,
  scannerPos = -1,
  cleavageActive = false,
  rotationSpeed = 0.25,
}) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * rotationSpeed;
    }
  });

  const numBases = sequence.length;
  const radius = 1.35;
  const heightStep = 0.32;
  const angleStep = Math.PI / 5.5; // ~32.7 degrees per base pair (~11 bp per full turn)

  // Compute backbone curve points
  const { curvePoints1, curvePoints2, basePairsData } = useMemo(() => {
    const pts1: THREE.Vector3[] = [];
    const pts2: THREE.Vector3[] = [];
    const bpData = [];

    for (let i = 0; i < numBases; i++) {
      const base1 = sequence[i]?.toUpperCase() in NUC_COLORS ? sequence[i].toUpperCase() : 'A';
      const base2 = COMPLEMENT[base1] || 'T';

      const y = (i - numBases / 2) * heightStep;
      const angle = i * angleStep;

      // Strand 1 (Sense 5' -> 3')
      const x1 = Math.cos(angle) * radius;
      const z1 = Math.sin(angle) * radius;

      // Strand 2 (Antisense 3' -> 5')
      const x2 = Math.cos(angle + Math.PI) * radius;
      const z2 = Math.sin(angle + Math.PI) * radius;

      pts1.push(new THREE.Vector3(x1, y, z1));
      pts2.push(new THREE.Vector3(x2, y, z2));

      bpData.push({
        i,
        y,
        angle,
        x1,
        z1,
        x2,
        z2,
        base1,
        base2,
      });
    }

    return { curvePoints1: pts1, curvePoints2: pts2, basePairsData: bpData };
  }, [sequence, numBases]);

  // Create smooth backbone curves
  const backboneCurve1 = useMemo(() => {
    if (curvePoints1.length < 2) return null;
    return new THREE.CatmullRomCurve3(curvePoints1);
  }, [curvePoints1]);

  const backboneCurve2 = useMemo(() => {
    if (curvePoints2.length < 2) return null;
    return new THREE.CatmullRomCurve3(curvePoints2);
  }, [curvePoints2]);

  return (
    <group ref={groupRef} position={[0, 0, 0]}>
      {/* Continuous Sugar-Phosphate Backbone Strand 1 (Cyan/Teal) */}
      {backboneCurve1 && (
        <mesh>
          <tubeGeometry args={[backboneCurve1, 100, 0.055, 8, false]} />
          <meshStandardMaterial
            color="#22d3ee"
            emissive="#0891b2"
            emissiveIntensity={0.35}
            roughness={0.25}
            metalness={0.5}
          />
        </mesh>
      )}

      {/* Continuous Sugar-Phosphate Backbone Strand 2 (Indigo/Purple) */}
      {backboneCurve2 && (
        <mesh>
          <tubeGeometry args={[backboneCurve2, 100, 0.055, 8, false]} />
          <meshStandardMaterial
            color="#818cf8"
            emissive="#4f46e5"
            emissiveIntensity={0.35}
            roughness={0.25}
            metalness={0.5}
          />
        </mesh>
      )}

      {/* Base Pairs (Connecting Rungs + Nucleotide Spheres) */}
      {basePairsData.map((bp) => {
        const { i, y, angle, x1, z1, x2, z2, base1, base2 } = bp;

        const isPam = highlightPam && i >= 20 && i <= 22;
        const isGuide = highlightGuide && i >= 0 && i < 20;
        const isCleavageLocus = cleavageActive && i === 17;
        const isScanned = scannerPos >= 0 && Math.abs(scannerPos - i) < 2;

        const base1Color = isPam
          ? '#f97316'
          : isGuide
          ? '#22d3ee'
          : isCleavageLocus
          ? '#ef4444'
          : NUC_COLORS[base1] || '#94a3b8';

        const base2Color = isPam
          ? '#f97316'
          : isGuide
          ? '#0ea5e9'
          : isCleavageLocus
          ? '#ef4444'
          : NUC_COLORS[base2] || '#94a3b8';

        return (
          <group key={`bp-group-${i}`} position={[0, y, 0]}>
            {/* Strand 1 Backbone Sphere Node */}
            <mesh position={[x1, 0, z1]}>
              <sphereGeometry args={[0.13, 16, 16]} />
              <meshStandardMaterial
                color={isPam ? '#f97316' : isGuide ? '#22d3ee' : '#0284c7'}
                emissive={isPam ? '#ea580c' : isGuide ? '#0891b2' : '#0369a1'}
                emissiveIntensity={isPam || isGuide || isScanned ? 0.9 : 0.3}
                roughness={0.2}
                metalness={0.4}
              />
            </mesh>

            {/* Strand 2 Backbone Sphere Node */}
            <mesh position={[x2, 0, z2]}>
              <sphereGeometry args={[0.13, 16, 16]} />
              <meshStandardMaterial
                color={isPam ? '#f97316' : isGuide ? '#818cf8' : '#4338ca'}
                emissive={isPam ? '#ea580c' : isGuide ? '#4f46e5' : '#3730a3'}
                emissiveIntensity={isPam || isGuide || isScanned ? 0.9 : 0.3}
                roughness={0.2}
                metalness={0.4}
              />
            </mesh>

            {/* Base Pair Connecting Rung Cylinder */}
            <mesh rotation={[0, -angle, Math.PI / 2]}>
              <cylinderGeometry args={[0.038, 0.038, radius * 2 - 0.15, 8]} />
              <meshStandardMaterial
                color={isPam ? '#ea580c' : isGuide ? '#0e7490' : '#475569'}
                emissive={isPam ? '#c2410c' : isGuide ? '#0891b2' : '#1e293b'}
                emissiveIntensity={isPam || isGuide ? 0.5 : 0.15}
                roughness={0.4}
              />
            </mesh>

            {/* Nucleotide 1 Bead */}
            <mesh position={[x1 * 0.45, 0, z1 * 0.45]}>
              <sphereGeometry args={[0.11, 14, 14]} />
              <meshStandardMaterial
                color={base1Color}
                emissive={base1Color}
                emissiveIntensity={isPam || isGuide || isScanned ? 0.8 : 0.25}
                roughness={0.3}
              />
            </mesh>

            {/* Nucleotide 2 Bead */}
            <mesh position={[x2 * 0.45, 0, z2 * 0.45]}>
              <sphereGeometry args={[0.11, 14, 14]} />
              <meshStandardMaterial
                color={base2Color}
                emissive={base2Color}
                emissiveIntensity={isPam || isGuide || isScanned ? 0.8 : 0.25}
                roughness={0.3}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
};
