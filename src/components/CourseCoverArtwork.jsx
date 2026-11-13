import React from 'react';

/**
 * ============================================================================
 * VOLTCORE APEX ACADEMIA — COURSE COVER ARTWORK COMPONENT
 * ============================================================================
 * Department of Electronics Engineering • MIT Campus • Anna University
 * Renders lightweight, theme-adaptive SVG engineering circuit/waveform cover
 * artwork backgrounds for course cards, hero banners, and lesson readers.
 * ============================================================================
 */

export function getCoverSvgForCourse(courseCode = '') {
  const code = (courseCode || '').toUpperCase().trim();

  // 1. Digital & VLSI
  if (['EC23C04', 'HDL6001', 'VLSI7001'].includes(code)) {
    return '/assets/covers/cover_digital_vlsi.svg';
  }
  // 2. Signals & DSP
  if (['EC23S01'].includes(code)) {
    return '/assets/covers/cover_signals_dsp.svg';
  }
  // 3. Embedded & IoT
  if (['EC23C06', 'IOT8701', 'STM32', 'STM32-ACADEMY', 'EC8702'].includes(code)) {
    return '/assets/covers/cover_embedded_iot.svg';
  }
  // 4. Communications & RF
  if (['EC23C08', 'EC23E04'].includes(code)) {
    return '/assets/covers/cover_comm_rf.svg';
  }
  // 5. Control & Electromagnetics
  if (['EC23C07'].includes(code)) {
    return '/assets/covers/cover_control_em.svg';
  }
  // 6. Analog & Devices (Default for EC23C01, EC23C02, EC23C03, EC23C05, etc.)
  return '/assets/covers/cover_analog_devices.svg';
}

export function getDomainEmblemForCourse(courseCode = '', domain = '') {
  if (domain) {
    const d = domain.toLowerCase();
    if (d.includes('digital') || d.includes('vlsi') || d.includes('fpga')) return '/assets/branding/emblem_digital_systems.svg';
    if (d.includes('signal') || d.includes('dsp') || d.includes('discrete')) return '/assets/branding/emblem_signal_processing.svg';
    if (d.includes('embed') || d.includes('iot') || d.includes('stm32') || d.includes('micro')) return '/assets/branding/emblem_embedded_iot.svg';
    if (d.includes('comm') || d.includes('rf') || d.includes('antenna')) return '/assets/branding/emblem_communication_systems.svg';
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

export default function CourseCoverArtwork({
  courseCode,
  domain,
  className = '',
  aspectRatio = '16/9',
  overlayOpacity = 0.55,
  showDomainBadge = false,
  children
}) {
  const coverUrl = domain ? `/assets/covers/cover_${domain}.svg` : getCoverSvgForCourse(courseCode);
  const emblemUrl = getDomainEmblemForCourse(courseCode, domain);

  return (
    <div
      className={`relative overflow-hidden rounded-2xl ${className}`}
      style={{
        aspectRatio,
        backgroundImage: `url(${coverUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Dark theme glassmorphic overlay */}
      <div
        className="absolute inset-0 bg-gradient-to-t from-[#020813] via-[#020813]/70 to-transparent pointer-events-none"
        style={{ opacity: overlayOpacity }}
      />

      {/* Floating Bespoke Domain Emblem Watermark Badge */}
      {showDomainBadge && (
        <div className="absolute top-3 right-3 z-20 w-10 h-10 rounded-xl bg-[#020813]/85 border border-[#00F0B5]/40 p-1.5 backdrop-blur-md shadow-lg pointer-events-none">
          <img
            src={emblemUrl}
            alt="Domain Emblem"
            className="w-full h-full object-contain"
          />
        </div>
      )}

      <div className="relative z-10 h-full w-full">
        {children}
      </div>
    </div>
  );
}
