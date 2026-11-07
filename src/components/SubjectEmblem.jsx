/**
 * ========================================================================================
 * VoltCore Apex Academia - Canva-Inspired ECE Subject Emblem Component
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/SubjectEmblem.jsx
 * Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Renders precision vector SVG circuit emblems for the 14 core ECE disciplines.
 * Supports theme-adaptive styling across all 18 vibrant color schemes.
 * ========================================================================================
 */

import React from 'react';
import { getSubjectMetadata } from '../data/subjectRegistry';

const SIZE_MAP = {
  sm: { box: 28, svg: 18, p: 'p-1', rounded: 'rounded-lg' },
  md: { box: 44, svg: 26, p: 'p-2', rounded: 'rounded-xl' },
  lg: { box: 64, svg: 38, p: 'p-3', rounded: 'rounded-2xl' },
  xl: { box: 88, svg: 52, p: 'p-4', rounded: 'rounded-3xl' },
  hero: { box: 120, svg: 72, p: 'p-6', rounded: 'rounded-3xl' },
};

export default function SubjectEmblem({
  courseCode,
  size = 'md',
  showFrame = true,
  interactive = false,
  glow = true,
  className = '',
  customColor = null,
}) {
  const meta = getSubjectMetadata(courseCode);
  const sizeConfig = SIZE_MAP[size] || SIZE_MAP.md;
  const activeColor = customColor || meta.primaryColor;

  return (
    <div
      className={`relative inline-flex items-center justify-center shrink-0 transition-transform ${
        interactive ? 'hover:scale-105 cursor-pointer' : ''
      } ${className}`}
      title={`${meta.name} (${meta.code}) - ${meta.symbolName}`}
      role="img"
      aria-label={meta.accessibleLabel}
    >
      {/* Outer Jewel Glow & Subtle Glass Frame */}
      {showFrame && (
        <div
          className={`absolute inset-0 ${sizeConfig.rounded} transition-all duration-300 pointer-events-none`}
          style={{
            background: `radial-gradient(circle at 50% 0%, ${activeColor}15, transparent 70%)`,
            border: `1px solid ${activeColor}35`,
            boxShadow: glow ? `0 0 16px ${activeColor}20` : 'none',
          }}
        />
      )}

      {/* Internal Vector Container */}
      <div
        className={`relative z-10 flex items-center justify-center ${sizeConfig.p}`}
        style={{
          width: `${sizeConfig.box}px`,
          height: `${sizeConfig.box}px`,
        }}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 48 48"
          width={sizeConfig.svg}
          height={sizeConfig.svg}
          style={{ color: activeColor }}
          className="transition-colors duration-300 drop-shadow-sm"
          dangerouslySetInnerHTML={{ __html: meta.svgPath }}
        />
      </div>

      {/* Pulsing Silicon Alignment Reticle (For Large/Hero views) */}
      {(size === 'lg' || size === 'xl' || size === 'hero') && (
        <span
          className="absolute -top-1 -right-1 flex h-2.5 w-2.5"
          title="Active Silicon Silicon Core"
        >
          <span
            className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            style={{ backgroundColor: activeColor }}
          />
          <span
            className="relative inline-flex rounded-full h-2.5 w-2.5"
            style={{ backgroundColor: activeColor }}
          />
        </span>
      )}
    </div>
  );
}
