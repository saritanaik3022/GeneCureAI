import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface GRNABindingProps {
  active: boolean;
  isScanning?: boolean;
  guideSequence?: string;
  /** 0-1: scanning progress along the DNA helix (used in scanning phase) */
  scanProgress?: number;
  /** 0-1: approach progress (0=far away, 1=fully docked on target strand) */
  approachProgress?: number;
  /** Starting Y position on helix when target is found */
  targetY?: number;
}

// RNA nucleotide colors (uracil replaces thymine in RNA; we use a rose palette)
const RNA_COLOR_SCANNING = '#f43f5e'; // bright rose/magenta
const RNA_COLOR_BINDING = '#22d3ee';  // cyan when bound to target
const RNA_EMISSIVE_SCANNING = '#be123c';
const RNA_EMISSIVE_BINDING = '#0891b2';

export const GRNABinding: React.FC<GRNABindingProps> = ({
  active,
  isScanning = false,
  guideSequence = 'GCAGCCAGATGCCTGGACAG',
  scanProgress = 0,
  approachProgress = 0,
  targetY = 0,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const pulseRef = useRef(0);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    pulseRef.current = clock.getElapsedTime();

    if (isScanning) {
      // Spiral scan: Move along the DNA helix path with offset from the helix
      const helixRadius = 2.5;
      const heightStep = 0.32;
      const numBases = 30;
      // scanProgress 0→1 corresponds to bottom→top of the displayed 30 bases
      const scanY = (-numBases / 2 + scanProgress * numBases) * heightStep;
      const angle = scanProgress * numBases * (Math.PI / 5.5); // follow helix angle
      
      // Position gRNA strand alongside (outside) the helix as it scans
      groupRef.current.position.x = Math.cos(angle) * helixRadius;
      groupRef.current.position.z = Math.sin(angle) * helixRadius;
      groupRef.current.position.y = scanY;
      // Face toward helix center
      groupRef.current.rotation.y = angle + Math.PI;
      // Slight oscillation to show "searching"
      groupRef.current.position.x += Math.sin(pulseRef.current * 3) * 0.15;
      groupRef.current.position.z += Math.cos(pulseRef.current * 3) * 0.15;

    } else if (active && approachProgress > 0) {
      // Approach phase: gRNA moves from scan orbit position inward to the target DNA strand
      // Start at radius 2.5, end at radius 1.35 (docked onto the helix strand)
      const startRadius = 2.5;
      const endRadius = 1.5;
      const currentRadius = startRadius + (endRadius - startRadius) * approachProgress;
      const dockAngle = Math.PI * 0.7; // fixed angle where the target protospacer sits

      groupRef.current.position.x = Math.cos(dockAngle) * currentRadius;
      groupRef.current.position.z = Math.sin(dockAngle) * currentRadius;
      groupRef.current.position.y = targetY;
      groupRef.current.rotation.y = dockAngle + Math.PI;
    }
  });

  if (!active && !isScanning) return null;

  const numBases = guideSequence.length;
  const heightStep = 0.32;
  const isBinding = !isScanning && approachProgress > 0.5;
  const color = isBinding ? RNA_COLOR_BINDING : RNA_COLOR_SCANNING;
  const emissive = isBinding ? RNA_EMISSIVE_BINDING : RNA_EMISSIVE_SCANNING;

  return (
    <group ref={groupRef} position={[2.5, 0, 0]}>
      {/* Guide RNA single-stranded ribbon */}
      {Array.from({ length: numBases }).map((_, i) => {
        const y = (i - numBases / 2) * heightStep;
        return (
          <group key={`grna-node-${i}`} position={[0, y, 0]}>
            {/* Ribonucleotide bead */}
            <mesh>
              <sphereGeometry args={[0.12, 16, 16]} />
              <meshStandardMaterial
                color={color}
                emissive={emissive}
                emissiveIntensity={isScanning ? 1.0 : 0.7}
                roughness={0.15}
                metalness={0.5}
              />
            </mesh>

            {/* Connecting rod between nucleotides */}
            {i < numBases - 1 && (
              <mesh position={[0, heightStep / 2, 0]}>
                <cylinderGeometry args={[0.03, 0.03, heightStep, 8]} />
                <meshStandardMaterial
                  color={color}
                  emissive={emissive}
                  emissiveIntensity={0.4}
                />
              </mesh>
            )}

            {/* Watson-Crick pairing arms when approaching target */}
            {isBinding && approachProgress > 0.7 && (
              <mesh position={[0.5 * (1 - approachProgress + 0.7), 0, 0]} rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[0.02, 0.02, 0.6 * approachProgress, 6]} />
                <meshStandardMaterial
                  color="#a5f3fc"
                  emissive="#22d3ee"
                  emissiveIntensity={0.6}
                  transparent
                  opacity={approachProgress}
                />
              </mesh>
            )}
          </group>
        );
      })}

      {/* Scan glow light */}
      <pointLight
        color={isBinding ? '#22d3ee' : '#f43f5e'}
        intensity={isScanning ? 2.5 : 1.5}
        distance={3}
      />
    </group>
  );
};
