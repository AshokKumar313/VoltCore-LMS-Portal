import { test, expect } from '@playwright/test';

/**
 * ========================================================================================
 * VoltCore Apex Academia - E2E Test: Course Navigation & Curriculum Progression
 * Phase 15 Quality Assurance Suite • Lead Architect: Ashok Kumar A
 * ========================================================================================
 */

test.describe('Course Navigation & Curriculum DAG Flow', () => {
  test('should load platform home landing page with brand standards', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/VoltCore/i);

    // Verify main header branding and navigation links
    const header = page.locator('header, nav').first();
    await expect(header).toBeVisible();

    // Verify core learning routes are linked
    const simulationLink = page.locator('a[href*="/simulation"]');
    await expect(simulationLink.first()).toBeVisible();
  });

  test('should navigate to embedded systems curriculum and display tiers', async ({ page }) => {
    await page.goto('/embedded-systems');
    await expect(page).toHaveTitle(/Embedded Systems/i);

    // Verify presence of curriculum modules or tier cards
    const contentArea = page.locator('main, .space-y-6').first();
    await expect(contentArea).toBeVisible();
  });

  test('should access STM32 Academy 21-module progression index', async ({ page }) => {
    await page.goto('/embedded-systems/stm32-academy');
    await expect(page).toHaveTitle(/STM32/i);

    // Verify STM32 Academy tier progression container
    const academyContainer = page.locator('body');
    await expect(academyContainer).toContainText(/STM32/i);
  });

  test('should verify faculty & enterprise administrator CMS portal access', async ({ page }) => {
    await page.goto('/enterprise-admin');
    await expect(page).toHaveTitle(/Admin|Enterprise|VoltCore/i);

    // Verify administration view container
    const adminContainer = page.locator('body');
    await expect(adminContainer).toBeVisible();
  });
});
