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

/**
 * Returns the dedicated 1-to-1 course-specific vector SVG logo path.
 * Covers all 14 Regulation 2023 ECE subjects plus Bare-Metal STM32 Academy.
 */
export function getCourseLogoPath(courseCode = '', subjectName = '') {
  const code = (courseCode || '').toUpperCase().trim();
  const name = (subjectName || '').toLowerCase().trim();

  // 1. Digital Signal Processing & Algorithms
  if (code === 'EC23S01' || name.includes('digital signal processing') || name.includes('dsp') || name.includes('algorithms')) {
    return '/assets/branding/logo_digital_signal_processing.svg';
  }
  // 2. Electronic Devices and Circuit Theory
  if (code === 'EC23C02' || code === 'EC23C03' || name.includes('electronic devices') || name.includes('semiconductor') || name.includes('circuit modeling')) {
    return '/assets/branding/logo_electronic_devices.svg';
  }
  // 3. Signals and Systems Analysis
  if (code === 'EC23C04' || name.includes('signals and systems') || name.includes('linear systems theory')) {
    return '/assets/branding/logo_signals_and_systems.svg';
  }
  // 4. Analog Integrated Circuits Design
  if (code === 'EC23C05' || name.includes('analog integrated circuit') || name.includes('analog ic')) {
    return '/assets/branding/logo_analog_ic_design.svg';
  }
  // 5. Digital System Design and Microprocessors
  if (code === 'EC23C06' || name.includes('digital system design') || name.includes('digital logic design')) {
    return '/assets/branding/logo_digital_system_design.svg';
  }
  // 6. Linear Integrated Circuits and Applications
  if (name.includes('linear integrated circuits') || name.includes('linear ic')) {
    return '/assets/branding/logo_linear_ic_applications.svg';
  }
  // 7. Microcontroller Architecture and Interfacing
  if (code === 'EC8702' || name.includes('microcontroller architecture') || name.includes('interfacing') || name.includes('embedded real-time')) {
    return '/assets/branding/logo_microcontroller_interfacing.svg';
  }
  // 8. Control Systems Engineering
  if (code === 'EC23C07' || name.includes('control systems')) {
    return '/assets/branding/logo_control_systems.svg';
  }
  // 9. Digital Communication Systems
  if (code === 'EC23C08' || name.includes('digital communication') || name.includes('telecommunications & rf')) {
    return '/assets/branding/logo_digital_communication.svg';
  }
  // 10. Advanced Communication Systems & 5G
  if (code === 'EC23E04' || name.includes('advanced communication') || name.includes('5g')) {
    return '/assets/branding/logo_advanced_communication_5g.svg';
  }
  // 11. Ad Hoc and Wireless Sensor Networks
  if (code === 'WSN8702' || name.includes('wireless sensor') || name.includes('ad hoc')) {
    return '/assets/branding/logo_wireless_sensor_networks.svg';
  }
  // 12. Internet of Things & Embedded Sensors
  if (code === 'IOT8701' || name.includes('internet of things') || name.includes('iot') || name.includes('embedded sensors')) {
    return '/assets/branding/logo_iot_embedded_sensors.svg';
  }
  // 13. Verilog HDL & FPGA System Prototyping
  if (code === 'HDL6001' || name.includes('verilog') || name.includes('fpga')) {
    return '/assets/branding/logo_verilog_hdl_fpga.svg';
  }
  // 14. CMOS VLSI Design & Nanometer Technology
  if (code === 'VLSI7001' || name.includes('cmos vlsi') || name.includes('vlsi design')) {
    return '/assets/branding/logo_cmos_vlsi_design.svg';
  }
  // 15. Bare-Metal STM32 Academy
  if (code === 'STM32' || code === 'STM32-ACADEMY' || name.includes('stm32') || name.includes('bare-metal') || name.includes('arm cortex-m microcontroller')) {
    return '/assets/branding/logo_stm32_baremetal_academy.svg';
  }
  // Circuit Analysis & Network Synthesis (Tier 1 Foundation fallback)
  if (code === 'EC23C01' || name.includes('circuit analysis') || name.includes('network synthesis')) {
    return '/assets/branding/logo_signals_and_systems.svg';
  }

  return getDomainEmblemPath(courseCode);
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
  const dedicatedLogoPath = getCourseLogoPath(courseCode, displayName);
  const shouldRenderBespoke = (useBespokeAsset || size === 'md' || size === 'lg' || size === 'xl' || size === 'hero') && !hasImgError;

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
            src={dedicatedLogoPath}
            alt={`${displayName} Logo`}
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
