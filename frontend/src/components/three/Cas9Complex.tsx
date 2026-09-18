import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface Cas9ComplexProps {
  visible: boolean;
}

export const Cas9Complex: React.FC<Cas9ComplexProps> = ({ visible }) => {
  const complexRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (complexRef.current && visible) {
      complexRef.current.rotation.y += delta * 0.15;
    }
  });

  if (!visible) return null;

  return (
    <group ref={complexRef} position={[0, 0, 0]}>
      {/* REC Lobe (Recognition Lobe - Cyan/Teal transparent envelope) */}
      <mesh position={[-0.8, 0.5, 0]}>
        <sphereGeometry args={[2.2, 24, 24]} />
        <meshStandardMaterial
          color="#0ea5e9"
          emissive="#0284c7"
          emissiveIntensity={0.15}
          roughness={0.4}
          metalness={0.2}
          transparent
          opacity={0.22}
          wireframe={false}
        />
      </mesh>

      {/* NUC Lobe (Nuclease Lobe - HNH and RuvC Catalytic Domains) */}
      <mesh position={[0.8, -0.4, 0]}>
        <sphereGeometry args={[2.0, 24, 24]} />
        <meshStandardMaterial
          color="#6366f1"
          emissive="#4f46e5"
          emissiveIntensity={0.15}
          roughness={0.4}
          metalness={0.2}
          transparent
          opacity={0.20}
        />
      </mesh>

      {/* RuvC Active Cleavage Center Marker (Orange/Amber) */}
      <mesh position={[0.6, 0.2, 0.9]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial
          color="#f97316"
          emissive="#ea580c"
          emissiveIntensity={1.2}
        />
      </mesh>

      {/* HNH Active Cleavage Center Marker (Cyan/Teal) */}
      <mesh position={[-0.5, 0.2, -0.9]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial
          color="#22d3ee"
          emissive="#06b6d4"
          emissiveIntensity={1.2}
        />
      </mesh>
    </group>
  );
};
