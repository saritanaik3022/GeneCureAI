import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface CleavageSiteProps {
  active: boolean;
}

export const CleavageSite: React.FC<CleavageSiteProps> = ({ active }) => {
  const markerRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!active || !markerRef.current) return;
    const t = clock.getElapsedTime();
    const scale = 1 + Math.sin(t * 4) * 0.15;
    markerRef.current.scale.set(scale, scale, scale);
  });

  if (!active) return null;

  return (
    <group ref={markerRef} position={[0, 0.35 * 2, 0]}>
      {/* Cleavage site indicator ring (-3 bp relative to PAM) */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.6, 0.06, 16, 32]} />
        <meshStandardMaterial
          color="#ef4444"
          emissive="#dc2626"
          emissiveIntensity={2.0}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Sparks/Energy marker at predicted cut site */}
      <pointLight color="#ef4444" intensity={4.0} distance={3} />
    </group>
  );
};
