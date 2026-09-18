import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface TOPSISSpaceProps {
  visible: boolean;
}

export const TOPSISSpace: React.FC<TOPSISSpaceProps> = ({ visible }) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (groupRef.current && visible) {
      groupRef.current.rotation.y += delta * 0.1;
    }
  });

  if (!visible) return null;

  // Criteria Coordinate Axes (On-Target, Off-Target Safety, Cancer Relevance, GC Optimality)
  const axes = [
    { dir: [1, 0, 0], color: '#38bdf8', label: 'On-Target (35%)' },
    { dir: [0, 1, 0], color: '#10b981', label: 'Off-Target Safety (30%)' },
    { dir: [0, 0, 1], color: '#f59e0b', label: 'Cancer Relevance (20%)' },
    { dir: [-0.7, -0.7, 0], color: '#a855f7', label: 'GC Optimality (15%)' },
  ];

  // Stylized Candidate Guides scattered in multi-attribute Euclidean space
  const candidates = [
    { pos: [1.8, 1.9, 1.7], rank: 1, color: '#22d3ee' },
    { pos: [1.5, 1.4, 1.2], rank: 2, color: '#60a5fa' },
    { pos: [0.9, 1.6, 1.1], rank: 3, color: '#93c5fd' },
    { pos: [0.4, 0.5, 0.8], rank: 4, color: '#64748b' },
  ];

  return (
    <group ref={groupRef}>
      {/* Criteria Axes */}
      {axes.map((ax, idx) => (
        <group key={`ax-${idx}`}>
          <arrowHelper
            args={[
              new THREE.Vector3(...ax.dir as [number, number, number]).normalize(),
              new THREE.Vector3(0, 0, 0),
              3.2,
              ax.color,
              0.3,
              0.15,
            ]}
          />
        </group>
      ))}

      {/* Positive Ideal Solution Point (A+) */}
      <mesh position={[2.2, 2.2, 2.2]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial
          color="#10b981"
          emissive="#059669"
          emissiveIntensity={1.8}
        />
      </mesh>

      {/* Negative Ideal Solution Point (A-) */}
      <mesh position={[-0.2, -0.2, -0.2]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial
          color="#ef4444"
          emissive="#dc2626"
          emissiveIntensity={1.8}
        />
      </mesh>

      {/* Ranked Candidates */}
      {candidates.map((c) => (
        <group key={`cand-${c.rank}`} position={c.pos as [number, number, number]}>
          <mesh>
            <sphereGeometry args={[0.15, 12, 12]} />
            <meshStandardMaterial
              color={c.color}
              emissive={c.color}
              emissiveIntensity={1.0}
            />
          </mesh>
        </group>
      ))}
    </group>
  );
};
