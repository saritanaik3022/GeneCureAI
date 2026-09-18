import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface MLDataFlowProps {
  visible: boolean;
}

export const MLDataFlow: React.FC<MLDataFlowProps> = ({ visible }) => {
  const groupRef = useRef<THREE.Group>(null);
  const particleGroupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (particleGroupRef.current && visible) {
      particleGroupRef.current.children.forEach((child, i) => {
        child.position.y += delta * (1.8 + (i % 4) * 0.4);
        if (child.position.y > 3.2) {
          child.position.y = -3.2;
        }
      });
    }
  });

  if (!visible) return null;

  // Real 5-layer ML data flow visualization
  const layers = [
    { label: '30-nt Sequence One-Hot (4x30)', y: -2.6, nodes: 4, color: '#38bdf8' },
    { label: '1D-CNN Convolutional Filters', y: -1.3, nodes: 6, color: '#818cf8' },
    { label: '64-dim Motif Embeddings', y: 0.0, nodes: 5, color: '#c084fc' },
    { label: '105 Engineered Bio-Features', y: 1.3, nodes: 7, color: '#fbbf24' },
    { label: 'Hybrid Stacking Meta-Learner (169-dim)', y: 2.6, nodes: 3, color: '#22d3ee' },
  ];

  return (
    <group ref={groupRef} position={[0, 0, 0]}>
      {layers.map((layer, lIdx) => (
        <group key={`layer-${lIdx}`} position={[0, layer.y, 0]}>
          {Array.from({ length: layer.nodes }).map((_, nIdx) => {
            const x = (nIdx - (layer.nodes - 1) / 2) * 0.85;
            return (
              <mesh key={`node-${lIdx}-${nIdx}`} position={[x, 0, 0]}>
                <boxGeometry args={[0.28, 0.28, 0.28]} />
                <meshStandardMaterial
                  color={layer.color}
                  emissive={layer.color}
                  emissiveIntensity={0.65}
                  roughness={0.25}
                  metalness={0.75}
                />
              </mesh>
            );
          })}
        </group>
      ))}

      {/* Flowing computation data particles */}
      <group ref={particleGroupRef}>
        {Array.from({ length: 24 }).map((_, pIdx) => {
          const x = ((pIdx % 6) - 2.5) * 0.65;
          const y = -3.2 + (pIdx / 24) * 6.4;
          const z = (Math.random() - 0.5) * 0.4;
          return (
            <mesh key={`p-${pIdx}`} position={[x, y, z]}>
              <sphereGeometry args={[0.055, 8, 8]} />
              <meshStandardMaterial
                color="#22d3ee"
                emissive="#06b6d4"
                emissiveIntensity={2.2}
              />
            </mesh>
          );
        })}
      </group>
    </group>
  );
};
