import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * ScientificMolecularBackground3D — subtle Three.js molecular particle field.
 * Renders faint animated DNA fragment ribbons and nucleotide particles.
 * Designed to be placed behind all other 3D content at low opacity.
 */
export const ScientificMolecularBackground3D: React.FC = () => {
  const particlesRef = useRef<THREE.Points>(null);
  const ribbonRef = useRef<THREE.Group>(null);
  const t = useRef(0);

  const particlePositions = useMemo(() => {
    const count = 280;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 24;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 24;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 24;
    }
    return positions;
  }, []);

  const helixPoints = useMemo(() => {
    // Background DNA ribbon — sparse, faint 3D helix
    const points: THREE.Vector3[] = [];
    for (let i = 0; i < 60; i++) {
      const angle = i * (Math.PI / 10);
      const y = (i / 60) * 18 - 9;
      points.push(new THREE.Vector3(Math.cos(angle) * 1.6, y, Math.sin(angle) * 1.6));
    }
    return points;
  }, []);

  const helixGeometry = useMemo(() => {
    const curve = new THREE.CatmullRomCurve3(helixPoints);
    return new THREE.TubeGeometry(curve, 100, 0.025, 4, false);
  }, [helixPoints]);

  useFrame((_, delta) => {
    t.current += delta;
    if (particlesRef.current) {
      particlesRef.current.rotation.y += delta * 0.04;
      particlesRef.current.rotation.x += delta * 0.015;
    }
    if (ribbonRef.current) {
      ribbonRef.current.rotation.y += delta * 0.07;
      ribbonRef.current.position.y = Math.sin(t.current * 0.2) * 0.5;
    }
  });

  return (
    <group>
      {/* Floating nucleotide particle cloud */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particlePositions.length / 3}
            array={particlePositions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.06}
          color="#38bdf8"
          transparent
          opacity={0.18}
          sizeAttenuation
          depthWrite={false}
        />
      </points>

      {/* Background DNA helix ribbon */}
      <group ref={ribbonRef} position={[-6, 0, -8]}>
        <mesh geometry={helixGeometry}>
          <meshStandardMaterial
            color="#22d3ee"
            transparent
            opacity={0.12}
            roughness={0.8}
            metalness={0.1}
          />
        </mesh>
      </group>

      {/* Second mirrored helix for depth */}
      <group position={[7, 0, -8]}>
        <mesh geometry={helixGeometry}>
          <meshStandardMaterial
            color="#818cf8"
            transparent
            opacity={0.09}
            roughness={0.8}
            metalness={0.1}
          />
        </mesh>
      </group>
    </group>
  );
};
