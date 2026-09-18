import React, { useEffect, useRef } from 'react';

interface ScientificMolecularBackgroundProps {
  /** Opacity multiplier for background intensity — default 1.0 */
  intensity?: number;
  /** Optional CSS class override */
  className?: string;
}

/**
 * ScientificMolecularBackground — High-fidelity 3D-perspective canvas DNA Double Helix background.
 * Renders recognizable winding B-DNA double-helix structures with nucleotide base-pair rungs,
 * glowing sugar-phosphate backbones, and subtle genomic particles.
 * Non-intrusive, pointer-events:none overlay that preserves text legibility.
 */
export const ScientificMolecularBackground: React.FC<ScientificMolecularBackgroundProps> = ({
  intensity = 1.0,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const BASES = ['A', 'T', 'G', 'C'];
    const BASE_COLORS: Record<string, string> = {
      A: '34, 197, 94',   // Emerald Green
      T: '239, 68, 68',   // Crimson Red
      G: '59, 130, 246',  // Sapphire Blue
      C: '234, 179, 8',   // Amber Yellow
    };

    interface FloatingParticle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      base: string;
      size: number;
      opacity: number;
      life: number;
    }

    interface HelixColumn {
      x: number;
      phase: number;
      rotSpeed: number;
      radius: number;
      pitch: number;
      alpha: number;
    }

    const particles: FloatingParticle[] = [];
    const helices: HelixColumn[] = [];

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };

    const initHelices = () => {
      helices.length = 0;
      const w = canvas.width;
      const count = Math.max(2, Math.min(4, Math.floor(w / 380)));
      for (let i = 0; i < count; i++) {
        helices.push({
          x: (w / (count + 1)) * (i + 1),
          phase: (i * Math.PI) / 2,
          rotSpeed: 0.006 + i * 0.002,
          radius: 38 + (i % 2) * 10,
          pitch: 180, // vertical wavelength in px
          alpha: (0.8 + (i % 2) * 0.3) * intensity,
        });
      }
    };

    const spawnParticle = () => {
      if (particles.length > 50) return;
      const base = BASES[Math.floor(Math.random() * BASES.length)];
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.25,
        vy: -0.15 - Math.random() * 0.2,
        base,
        size: 7 + Math.random() * 4,
        opacity: 0,
        life: 0,
      });
    };

    let globalT = 0;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      globalT += 0.015;

      // Draw each 3D DNA double helix column
      for (const helix of helices) {
        helix.phase += helix.rotSpeed;

        const h = canvas.height;
        const totalBasePairs = Math.ceil(h / 16); // 1 rung every 16 pixels
        const rungs: {
          y: number;
          x1: number;
          z1: number;
          x2: number;
          z2: number;
          baseA: string;
          baseB: string;
        }[] = [];

        // Precompute points along the helix
        for (let i = 0; i <= totalBasePairs; i++) {
          const y = i * 16;
          const theta = helix.phase + (y / helix.pitch) * (Math.PI * 2);

          // 3D coordinates: x along screen, z in depth [-1, 1]
          const cosVal = Math.cos(theta);
          const sinVal = Math.sin(theta);

          const x1 = helix.x + cosVal * helix.radius;
          const z1 = sinVal; // front > 0, back < 0

          const x2 = helix.x - cosVal * helix.radius;
          const z2 = -sinVal;

          const basePairIndex = i % 4;
          const baseA = basePairIndex === 0 ? 'A' : basePairIndex === 1 ? 'G' : basePairIndex === 2 ? 'T' : 'C';
          const baseB = baseA === 'A' ? 'T' : baseA === 'T' ? 'A' : baseA === 'G' ? 'C' : 'G';

          rungs.push({ y, x1, z1, x2, z2, baseA, baseB });
        }

        // Draw Base Pair Rungs
        for (const rung of rungs) {
          // Average z-depth determines brightness & thickness
          const avgZ = (rung.z1 + rung.z2) / 2;
          const depthAlpha = Math.max(0.04, 0.09 + avgZ * 0.05) * helix.alpha;

          // Crossbar connector line
          ctx.beginPath();
          ctx.strokeStyle = `rgba(148, 163, 184, ${depthAlpha * 0.75})`;
          ctx.lineWidth = 1.0;
          ctx.moveTo(rung.x1, rung.y);
          ctx.lineTo(rung.x2, rung.y);
          ctx.stroke();

          // Nucleotide Node 1 (Strand A)
          const nodeAlpha1 = Math.max(0.06, 0.18 + rung.z1 * 0.12) * helix.alpha;
          const col1 = BASE_COLORS[rung.baseA] || '34, 211, 238';
          const rad1 = Math.max(1.5, 2.8 + rung.z1 * 1.2);

          ctx.beginPath();
          ctx.fillStyle = `rgba(${col1}, ${nodeAlpha1})`;
          ctx.arc(rung.x1, rung.y, rad1, 0, Math.PI * 2);
          ctx.fill();

          // Nucleotide Node 2 (Strand B)
          const nodeAlpha2 = Math.max(0.06, 0.18 + rung.z2 * 0.12) * helix.alpha;
          const col2 = BASE_COLORS[rung.baseB] || '129, 140, 248';
          const rad2 = Math.max(1.5, 2.8 + rung.z2 * 1.2);

          ctx.beginPath();
          ctx.fillStyle = `rgba(${col2}, ${nodeAlpha2})`;
          ctx.arc(rung.x2, rung.y, rad2, 0, Math.PI * 2);
          ctx.fill();
        }

        // Draw Continuous Sugar-Phosphate Backbone Strands
        // Strand 1 (Cyan)
        ctx.beginPath();
        ctx.strokeStyle = `rgba(34, 211, 238, ${0.12 * helix.alpha})`;
        ctx.lineWidth = 1.5;
        for (let i = 0; i < rungs.length; i++) {
          if (i === 0) ctx.moveTo(rungs[i].x1, rungs[i].y);
          else ctx.lineTo(rungs[i].x1, rungs[i].y);
        }
        ctx.stroke();

        // Strand 2 (Indigo/Purple)
        ctx.beginPath();
        ctx.strokeStyle = `rgba(168, 85, 247, ${0.10 * helix.alpha})`;
        ctx.lineWidth = 1.3;
        for (let i = 0; i < rungs.length; i++) {
          if (i === 0) ctx.moveTo(rungs[i].x2, rungs[i].y);
          else ctx.lineTo(rungs[i].x2, rungs[i].y);
        }
        ctx.stroke();
      }

      // Draw floating molecular particles & nucleotide identifiers
      if (Math.random() < 0.06) spawnParticle();

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life += 0.012;

        if (p.life < 0.2) p.opacity = p.life / 0.2;
        else if (p.life > 0.7) p.opacity = 1 - (p.life - 0.7) / 0.3;
        else p.opacity = 1;

        if (p.life >= 1) {
          particles.splice(i, 1);
          continue;
        }

        const color = BASE_COLORS[p.base] || '148, 163, 184';
        ctx.save();
        ctx.globalAlpha = p.opacity * 0.24 * intensity;
        ctx.font = `bold ${p.size}px 'JetBrains Mono', 'Courier New', monospace`;
        ctx.fillStyle = `rgba(${color}, 1)`;
        ctx.fillText(p.base, p.x, p.y);
        ctx.restore();
      }

      animRef.current = requestAnimationFrame(draw);
    };

    const resizeObserver = new ResizeObserver(() => {
      resize();
      initHelices();
    });

    resize();
    initHelices();
    draw();
    resizeObserver.observe(canvas);

    return () => {
      cancelAnimationFrame(animRef.current);
      resizeObserver.disconnect();
    };
  }, [intensity]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none select-none ${className}`}
      style={{ zIndex: 0 }}
      aria-hidden="true"
    />
  );
};
