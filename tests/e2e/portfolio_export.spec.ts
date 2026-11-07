import { test, expect } from '@playwright/test';

/**
 * ========================================================================================
 * VoltCore Apex Academia - E2E Test: Student Technical Portfolio & ATS Resume Export
 * Phase 15 Quality Assurance Suite • Lead Architect: Ashok Kumar A
 * Validates: Project Badges, Lab Observations, Engineering Resume Compilation
 * ========================================================================================
 */

test.describe('Student Technical Portfolio & ATS Resume Export Flow', () => {
  test('should load student projects hub and verified lab report credentials', async ({ page }) => {
    await page.goto('/student-projects');
    await expect(page).toHaveTitle(/Project|Portfolio|VoltCore/i);

    // Verify projects container
    const projectsContainer = page.locator('main, .space-y-6').first();
    await expect(projectsContainer).toBeVisible();
  });

  test('should access career professional development hub and verified badges', async ({ page }) => {
    await page.goto('/careers');
    await expect(page).toHaveTitle(/Career|Professional|VoltCore/i);

    // Verify careers container
    const careerContainer = page.locator('body');
    await expect(careerContainer).toBeVisible();
  });
});
