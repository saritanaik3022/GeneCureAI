import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface SequenceScannerProps {
  active: boolean;
  totalLength?: number;
  /** External scan position 0-1 (overrides internal animation when provided) */
  scanProgress?: number;
}

export const SequenceScanner: React.FC<SequenceScannerProps> = ({
  active,
  totalLength = 30,
  scanProgress,
}) => {
  const ringRef = useRef<THREE.Mesh>(null);
  const lightRef = useRef<THREE.PointLight>(null);
  const internalPosRef = useRef(0);

  const heightStep = 0.32;
  const minY = (-totalLength / 2) * heightStep;
  const maxY = (totalLength / 2) * heightStep;
  const totalRange = maxY - minY;

  useFrame((_, delta) => {
    if (!active || !ringRef.current) return;

    let currentY: number;

    if (scanProgress !== undefined) {
      // Externally driven progress (0→1)
      currentY = minY + scanProgress * totalRange;
    } else {
      // Auto-animate: sweep upward and loop
      internalPosRef.current += delta * 3;
      if (internalPosRef.current > totalRange) {
        internalPosRef.current = 0;
      }
      currentY = minY + internalPosRef.current;
    }

    ringRef.current.position.y = currentY;
    if (lightRef.current) {
      lightRef.current.position.y = currentY;
    }
  });

  if (!active) return null;

  return (
    <group>
      {/* Scanning Ring — sits flush against helix, sweeping up/down */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <torusGeometry args={[1.9, 0.05, 16, 64]} />
        <meshStandardMaterial
          color="#22d3ee"
          emissive="#22d3ee"
          emissiveIntensity={2.8}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Outer halo ring for visual depth */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <torusGeometry args={[2.15, 0.02, 8, 48]} />
        <meshStandardMaterial
          color="#0ea5e9"
          emissive="#0ea5e9"
          emissiveIntensity={1.5}
          transparent
          opacity={0.45}
        />
      </mesh>

      {/* Scan Light */}
      <pointLight
        ref={lightRef}
        color="#22d3ee"
        intensity={4.0}
        distance={5}
        position={[0, 0, 0]}
      />
    </group>
  );
};
