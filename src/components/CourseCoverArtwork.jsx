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
  const code = (courseCode || '').toUpperCase().trim();
  const d = (domain || '').toLowerCase().trim();

  // 1. Digital Signal Processing & Algorithms
  if (code === 'EC23S01' || d.includes('signal processing') || d.includes('dsp') || d.includes('algorithm')) {
    return '/assets/branding/logo_digital_signal_processing.svg';
  }
  // 2. Electronic Devices and Circuit Theory
  if (code === 'EC23C02' || code === 'EC23C03' || d.includes('electronic devices') || d.includes('semiconductor') || d.includes('circuit modeling')) {
    return '/assets/branding/logo_electronic_devices.svg';
  }
  // 3. Signals and Systems Analysis
  if (code === 'EC23C04' || d.includes('signals and systems') || d.includes('linear systems')) {
    return '/assets/branding/logo_signals_and_systems.svg';
  }
  // 4. Analog Integrated Circuits Design
  if (code === 'EC23C05' || d.includes('analog integrated') || d.includes('analog ic')) {
    return '/assets/branding/logo_analog_ic_design.svg';
  }
  // 5. Digital System Design and Microprocessors
  if (code === 'EC23C06' || d.includes('digital system design') || d.includes('digital logic')) {
    return '/assets/branding/logo_digital_system_design.svg';
  }
  // 6. Linear Integrated Circuits and Applications
  if (d.includes('linear integrated') || d.includes('linear ic')) {
    return '/assets/branding/logo_linear_ic_applications.svg';
  }
  // 7. Microcontroller Architecture and Interfacing
  if (code === 'EC8702' || d.includes('microcontroller') || d.includes('interfacing') || d.includes('embedded real-time')) {
    return '/assets/branding/logo_microcontroller_interfacing.svg';
  }
  // 8. Control Systems Engineering
  if (code === 'EC23C07' || d.includes('control systems') || d.includes('control')) {
    return '/assets/branding/logo_control_systems.svg';
  }
  // 9. Digital Communication Systems
  if (code === 'EC23C08' || d.includes('digital communication') || d.includes('telecommunication')) {
    return '/assets/branding/logo_digital_communication.svg';
  }
  // 10. Advanced Communication Systems & 5G
  if (code === 'EC23E04' || d.includes('advanced communication') || d.includes('5g')) {
    return '/assets/branding/logo_advanced_communication_5g.svg';
  }
  // 11. Ad Hoc and Wireless Sensor Networks
  if (code === 'WSN8702' || d.includes('wireless sensor') || d.includes('ad hoc')) {
    return '/assets/branding/logo_wireless_sensor_networks.svg';
  }
  // 12. Internet of Things & Embedded Sensors
  if (code === 'IOT8701' || d.includes('iot') || d.includes('internet of things') || d.includes('sensor')) {
    return '/assets/branding/logo_iot_embedded_sensors.svg';
  }
  // 13. Verilog HDL & FPGA System Prototyping
  if (code === 'HDL6001' || d.includes('verilog') || d.includes('fpga')) {
    return '/assets/branding/logo_verilog_hdl_fpga.svg';
  }
  // 14. CMOS VLSI Design & Nanometer Technology
  if (code === 'VLSI7001' || d.includes('vlsi') || d.includes('cmos')) {
    return '/assets/branding/logo_cmos_vlsi_design.svg';
  }
  // 15. Bare-Metal STM32 Academy
  if (code === 'STM32' || code === 'STM32-ACADEMY' || d.includes('stm32') || d.includes('bare-metal') || d.includes('arm cortex-m')) {
    return '/assets/branding/logo_stm32_baremetal_academy.svg';
  }
  // Fallbacks
  if (code === 'EC23C01') {
    return '/assets/branding/logo_signals_and_systems.svg';
  }

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
