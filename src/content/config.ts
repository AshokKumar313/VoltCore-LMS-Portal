import { defineCollection, z } from 'astro:content';

/**
 * VoltCore Apex Academia - Content Collections Schema
 * Core Engineering Series • Autonomous Engineering Cluster
 */

// 1. Curriculum Modules (Advanced Specialization Tracks & Core Syllabi)
const modulesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    code: z.string(), // e.g. "IOT8701", "AUTO8702", "EC8702"
    semester: z.number().min(1).max(8),
    regulation: z.string().default('Core Engineering Series'),
    department: z.string().default('Autonomous Engineering Cluster'),
    credits: z.number().min(1).max(6),
    order: z.number(),
    description: z.string(),
    difficulty: z.enum(['Fundamental', 'Intermediate', 'Advanced', 'Apex Research']).default('Advanced'),
    author: z.string().default('VoltCore Silicon Architecture Team'),
    publishDate: z.coerce.date(),
    prerequisites: z.array(z.string()).default([]),
    learningOutcomes: z.array(z.string()),
    hardwareKit: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    specializationTrack: z.string().optional(),
    simulationComponent: z.string().optional(),
    trackSlug: z.string().optional(),
    syllabusUnits: z.array(z.object({
      unit: z.number(),
      title: z.string(),
      topics: z.array(z.string()),
      labHours: z.number().default(4),
    })).optional(),
    ieeeReference: z.string().optional(),
    xpReward: z.number().default(250),
  }),
});

// 2. Hardware Component Specifications (Datasheets, Pinouts, Electrical Specs)
const componentsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    partNumber: z.string(),
    category: z.enum([
      'Microcontroller',
      'Sensor',
      'Transceiver',
      'Display',
      'Actuator',
      'Power',
      'Software Kernel'
    ]),
    operatingVoltage: z.string(), // e.g. "3.3V DC (2.7V - 3.6V)"
    currentDraw: z.string(), // e.g. "Active: 80-240 mA, Deep Sleep: 10 uA"
    interfaces: z.array(z.enum([
      'SPI',
      'I2C',
      'UART',
      'CAN',
      'PWM',
      'ADC',
      'DAC',
      'GPIO',
      'Wi-Fi 802.11 b/g/n',
      'BLE 4.2'
    ])),
    pinout: z.array(z.object({
      pin: z.union([z.string(), z.number()]),
      name: z.string(),
      type: z.enum([
        'Power',
        'Ground',
        'Digital I/O',
        'Analog In',
        'Bus Clock',
        'Bus Data',
        'Reset',
        'Chip Select'
      ]),
      description: z.string(),
    })).default([]),
    datasheetUrl: z.string(),
    wokwiPartId: z.string().optional(),
    architecture: z.string().optional(),
    clockSpeed: z.string().optional(),
    description: z.string(),
    labLocation: z.string().default('Advanced Embedded Systems Laboratory - Station B'),
  }),
});

// 3. Wokwi Simulation Topologies (Virtual Breadboard, diagram.json, and Firmware)
const simulationsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    difficulty: z.enum(['Beginner', 'Intermediate', 'Advanced', 'Industry Apex']),
    estimatedMinutes: z.number().default(30),
    author: z.string().default('VoltCore Silicon Architecture Team'),
    wokwiId: z.string().optional(), // Wokwi project URL slug or ID
    verifiedOnHardware: z.boolean().default(true),
    hardwarePlatform: z.enum([
      'ESP32',
      'Raspberry Pi Pico',
      'STM32 Nucleo',
      'Arduino Uno R3',
      'ARM Cortex-M4'
    ]).default('ESP32'),
    chipList: z.array(z.string()),
    wiringConnections: z.array(z.object({
      from: z.string(),
      to: z.string(),
      color: z.string().default('cyan'),
      signal: z.string().optional(),
    })).default([]),
    learningObjectives: z.array(z.string()),
    defaultSketch: z.string(),
    diagramJson: z.union([z.record(z.any()), z.string()]),
    expectedTelemetry: z.record(z.any()).optional(),
  }),
});

// 4. STM32 Academy 21-Module Bare-Metal & RTOS Curriculum
const stm32AcademyCollection = defineCollection({
  type: 'content',
  schema: z.object({
    moduleNumber: z.number().min(1).max(21),
    title: z.string(),
    shortTitle: z.string().optional(),
    tier: z.enum([
      'Tier 1: Architecture & Toolchain',
      'Tier 2: Core Peripherals',
      'Tier 3: Serial Buses & DMA',
      'Tier 4: RTOS & Kernel Internals',
      'Tier 5: Industrial Hardware & Edge AI'
    ]),
    difficulty: z.enum(['Fundamental', 'Intermediate', 'Advanced', 'Apex Expert']),
    boardTargets: z.array(z.enum([
      'Nucleo-F401RE',
      'Blue Pill (STM32F103C8T6)',
      'STM32F4-Discovery',
      'Universal ARM Cortex-M'
    ])),
    prerequisites: z.array(z.string()).default([]),
    estimatedDuration: z.string(), // e.g. "45 mins", "1.5 hours"
    cortexArchitecture: z.enum(['Cortex-M3', 'Cortex-M4F', 'Universal Cortex-M']).default('Cortex-M4F'),
    registerFocus: z.array(z.string()).default([]),
    description: z.string(),
    keyFormulas: z.array(z.string()).default([]),
    hardwareApparatus: z.array(z.string()).default([]),
    order: z.number(),
    xpReward: z.number().default(150),
    author: z.string().default('VoltCore Silicon Architecture Team'),
    publishDate: z.coerce.date().default(() => new Date()),
  }),
});

export const collections = {
  modules: modulesCollection,
  components: componentsCollection,
  simulations: simulationsCollection,
  'stm32-academy': stm32AcademyCollection,
};

