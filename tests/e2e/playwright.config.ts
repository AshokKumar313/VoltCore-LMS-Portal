import { defineConfig, devices } from '@playwright/test';

/**
 * ========================================================================================
 * VoltCore Apex Academia - Playwright E2E Automation Configuration (Phase 15)
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * Lead Systems Architect & Quality Assurance Director: Ashok Kumar A
 * Host Target: HP Victus 15-fa2xxx (LAPTOP-3NEGBVLE) • Passive CPU Target (<5%)
 * ========================================================================================
 */

export default defineConfig({
  testDir: './',
  testMatch: '**/*.spec.ts',
  timeout: 45000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: false, // Low concurrency to preserve HP Victus laptop thermal profile
  workers: 1, // Single worker avoids multi-core thermal throttling
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:4321',
    headless: true, // Headless mode with zero graphical overhead
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
  },

  projects: [
    {
      name: 'Desktop Chromium Headless',
      use: {
        ...devices['Desktop Chrome'],
        headless: true,
        launchOptions: {
          args: [
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',
          ],
        },
      },
    },
  ],

  webServer: {
    command: 'npm run preview -- --port 4321',
    url: 'http://localhost:4321',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
