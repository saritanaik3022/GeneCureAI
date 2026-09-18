import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface OffTargetGenomeProps {
  visible: boolean;
  offTargetSites?: Array<{
    chromosome: string;
    position: number;
    strand: string;
    mismatches: number;
    cfd_score?: number | null;
    risk_level?: string;
  }>;
}

export const OffTargetGenome: React.FC<OffTargetGenomeProps> = ({
  visible,
  offTargetSites = [],
}) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (groupRef.current && visible) {
      groupRef.current.rotation.y += delta * 0.15;
    }
  });

  // Chromosome ribbon ring positions (simplified 23 chromosome layout)
  const chromosomePositions = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const count = 23;
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const radius = 4.0;
      positions.push(new THREE.Vector3(
        Math.cos(angle) * radius,
        (i % 5 - 2) * 0.6,
        Math.sin(angle) * radius
      ));
    }
    return positions;
  }, []);

  if (!visible) return null;

  const riskColor = (risk?: string) => {
    if (risk === 'HIGH') return '#ef4444';
    if (risk === 'MEDIUM') return '#f97316';
    return '#22c55e';
  };

  const hasRealData = offTargetSites.length > 0;

  return (
    <group ref={groupRef}>
      {/* Chromosome ribbons arranged in a ring */}
      {chromosomePositions.map((pos, i) => (
        <mesh key={`chr-${i}`} position={pos}>
          <cylinderGeometry args={[0.12, 0.12, 1.2 + Math.random() * 0.6, 8]} />
          <meshStandardMaterial
            color="#334155"
            emissive="#1e293b"
            emissiveIntensity={0.2}
            roughness={0.6}
            metalness={0.3}
          />
        </mesh>
      ))}

      {/* Real off-target loci markers */}
      {hasRealData && offTargetSites.slice(0, 30).map((site, idx) => {
        // Map chromosome to ring position
        const chrNum = parseInt(site.chromosome.replace(/[^0-9]/g, '')) || 1;
        const ringIdx = Math.min(chrNum - 1, chromosomePositions.length - 1);
        const basePos = chromosomePositions[ringIdx] || chromosomePositions[0];
        const markerPos = new THREE.Vector3(basePos.x, basePos.y + (site.mismatches * 0.2 - 0.3), basePos.z);
        const color = riskColor(site.risk_level);

        return (
          <mesh key={`ot-site-${idx}`} position={markerPos}>
            <sphereGeometry args={[0.16, 12, 12]} />
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={0.9}
              roughness={0.1}
              metalness={0.6}
            />
          </mesh>
        );
      })}

      {/* No real data fallback: show dimmed placeholder */}
      {!hasRealData && (
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[1.0, 16, 16]} />
          <meshStandardMaterial
            color="#1e293b"
            wireframe={true}
            opacity={0.3}
            transparent
          />
        </mesh>
      )}
    </group>
  );
};
