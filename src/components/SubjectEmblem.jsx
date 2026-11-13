/**
 * ========================================================================================
 * VoltCore Apex Academia - Professional Canva-Inspired ECE Subject Emblem Component
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Module: src/components/SubjectEmblem.jsx
 * Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
 *
 * Renders precision vector SVG circuit emblems for the 14 core ECE disciplines.
 * Presents clean, professional engineering discipline names (no raw alphanumeric codes).
 * Supports theme-adaptive styling across all 18 vibrant color schemes.
 * ========================================================================================
 */

import React, { useState } from 'react';
import { getSubjectMetadata } from '../data/subjectRegistry';

const SIZE_MAP = {
  sm: { box: 28, svg: 18, p: 'p-1', rounded: 'rounded-lg' },
  md: { box: 44, svg: 26, p: 'p-2', rounded: 'rounded-xl' },
  lg: { box: 64, svg: 42, p: 'p-2.5', rounded: 'rounded-2xl' },
  xl: { box: 88, svg: 60, p: 'p-3', rounded: 'rounded-3xl' },
  hero: { box: 120, svg: 84, p: 'p-4', rounded: 'rounded-3xl' },
};

/**
 * Returns matching bespoke domain emblem vector SVG path.
 */
export function getDomainEmblemPath(courseCode = '', domain = '') {
  if (domain) {
    const d = domain.toLowerCase();
    if (d.includes('digital') || d.includes('vlsi') || d.includes('fpga')) return '/assets/branding/emblem_digital_systems.svg';
    if (d.includes('signal') || d.includes('dsp') || d.includes('discrete')) return '/assets/branding/emblem_signal_processing.svg';
    if (d.includes('embed') || d.includes('iot') || d.includes('stm32') || d.includes('micro')) return '/assets/branding/emblem_embedded_iot.svg';
    if (d.includes('comm') || d.includes('rf') || d.includes('antenna') || d.includes('optical')) return '/assets/branding/emblem_communication_systems.svg';
    if (d.includes('control') || d.includes('electro') || d.includes('field') || d.includes('trans')) return '/assets/branding/emblem_control_electromagnetics.svg';
    return '/assets/branding/emblem_analog_circuits.svg';
  }
  const code = (courseCode || '').toUpperCase().trim();
  if (['EC23C04', 'HDL6001', 'VLSI7001'].includes(code)) return '/assets/branding/emblem_digital_systems.svg';
  if (['EC23S01'].includes(code)) return '/assets/branding/emblem_signal_processing.svg';
  if (['EC23C06', 'IOT8701', 'STM32', 'STM32-ACADEMY', 'EC8702'].includes(code)) return '/assets/branding/emblem_embedded_iot.svg';
  if (['EC23C08', 'EC23E04'].includes(code)) return '/assets/branding/emblem_communication_systems.svg';
  if (['EC23C07'].includes(code)) return '/assets/branding/emblem_control_electromagnetics.svg';
  return '/assets/branding/emblem_analog_circuits.svg';
}

export default function SubjectEmblem({
  courseCode,
  domain = '',
  size = 'md',
  showFrame = true,
  interactive = false,
  glow = true,
  className = '',
  customColor = null,
  showLabel = false,
  labelPosition = 'bottom',
  useBespokeAsset = false,
}) {
  const [hasImgError, setHasImgError] = useState(false);
  const meta = getSubjectMetadata(courseCode);
  const sizeConfig = SIZE_MAP[size] || SIZE_MAP.md;
  const activeColor = customColor || meta.primaryColor;
  const displayName = meta.disciplineName || meta.name;
  const domainEmblemPath = getDomainEmblemPath(courseCode, domain || meta.industryDomain || meta.subfield);
  const shouldRenderBespoke = (useBespokeAsset || size === 'lg' || size === 'xl' || size === 'hero') && !hasImgError;

  const emblemNode = (
    <div
      className={`relative inline-flex items-center justify-center shrink-0 transition-transform ${
        interactive ? 'hover:scale-105 cursor-pointer' : ''
      } ${!showLabel ? className : ''}`}
      title={`${displayName} — ${meta.symbolName}`}
      role="img"
      aria-label={`${displayName} — ${meta.accessibleLabel}`}
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
        {shouldRenderBespoke ? (
          <img
            src={domainEmblemPath}
            alt={`${displayName} Emblem`}
            className="w-full h-full object-contain drop-shadow-sm transition-transform duration-300"
            onError={() => setHasImgError(true)}
          />
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 48 48"
            width={sizeConfig.svg}
            height={sizeConfig.svg}
            style={{ color: activeColor }}
            className="transition-colors duration-300 drop-shadow-sm"
            dangerouslySetInnerHTML={{ __html: meta.svgPath }}
          />
        )}
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

  if (!showLabel) {
    return emblemNode;
  }

  const isRow = labelPosition === 'right';

  return (
    <div
      className={`inline-flex ${isRow ? 'flex-row items-center gap-3' : 'flex-col items-center text-center gap-2'} ${className}`}
    >
      {emblemNode}
      <div className={isRow ? 'text-left' : 'text-center'}>
        <div
          className="text-xs sm:text-sm font-bold font-sans tracking-tight"
          style={{ color: 'var(--theme-text, #F8FAFC)' }}
        >
          {displayName}
        </div>
        {meta.subfield && (
          <div
            className="text-[10px] font-mono uppercase tracking-wider"
            style={{ color: 'var(--theme-text-muted, #94A3B8)' }}
          >
            {meta.subfield}
          </div>
        )}
      </div>
    </div>
  );
}
