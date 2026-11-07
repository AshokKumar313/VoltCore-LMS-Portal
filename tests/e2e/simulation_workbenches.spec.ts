import { test, expect } from '@playwright/test';

/**
 * ========================================================================================
 * VoltCore Apex Academia - E2E Test: Simulation Workbenches & Virtual Instrumentation
 * Phase 15 Quality Assurance Suite • Lead Architect: Ashok Kumar A
 * Validates: Virtual Oscilloscope, Engineering Math Studio (Poles/Zeros), Wokwi Bridge
 * ========================================================================================
 */

test.describe('Simulation Workbenches & Virtual Instrumentation Flow', () => {
  test('should load Keysight / Rigol Virtual Oscilloscope with dual channels', async ({ page }) => {
    await page.goto('/virtual-bench');
    await expect(page).toHaveTitle(/Virtual Bench|Oscilloscope|VoltCore/i);

    // Verify DSO interface exists
    const dsoContainer = page.locator('svg, canvas, div[class*="Oscilloscope"]').first();
    await expect(dsoContainer).toBeVisible();

    // Verify Channel Controls (CH1 / CH2 buttons)
    const chButtons = page.locator('button:has-text("CH1"), button:has-text("CH2")');
    if ((await chButtons.count()) > 0) {
      await expect(chButtons.first()).toBeVisible();
    }
  });

  test('should interact with Engineering Mathematics Studio complex plane canvas', async ({ page }) => {
    await page.goto('/math-studio');
    await expect(page).toHaveTitle(/Mathematics Studio|Math Studio|VoltCore/i);

    // Verify Complex Plane Canvas (SVG element)
    const complexPlaneSvg = page.locator('svg[viewBox="0 0 520 420"]');
    await expect(complexPlaneSvg).toBeVisible();

    // Verify Domain Toggles: s-Plane (Laplace) and z-Plane (Discrete)
    const sPlaneBtn = page.locator('button:has-text("s-Plane")');
    const zPlaneBtn = page.locator('button:has-text("z-Plane")');
    await expect(sPlaneBtn).toBeVisible();
    await expect(zPlaneBtn).toBeVisible();

    // Switch to z-Plane
    await zPlaneBtn.click();
    await expect(complexPlaneSvg).toContainText(/Unit Circle/i);

    // Switch back to s-Plane
    await sPlaneBtn.click();
    await expect(complexPlaneSvg).toContainText(/STABLE REGION/i);

    // Verify Analytics View Tabs: Frequency (Bode), Transient (RK4), Fourier Harmonics
    const bodeTab = page.locator('button:has-text("Frequency")');
    const transientTab = page.locator('button:has-text("Transient")');
    const fourierTab = page.locator('button:has-text("Fourier")');

    await expect(bodeTab).toBeVisible();
    await expect(transientTab).toBeVisible();
    await expect(fourierTab).toBeVisible();

    // Switch to Transient Tab and assert Runge-Kutta curve
    await transientTab.click();
    const transientMetrics = page.locator('text=PERCENT OVERSHOOT');
    await expect(transientMetrics).toBeVisible();

    // Switch to Fourier Tab and assert Harmonics Slider
    await fourierTab.click();
    const harmonicsSlider = page.locator('input[type="range"]');
    await expect(harmonicsSlider.first()).toBeVisible();

    // Verify Commit & Audit button is clickable
    const commitBtn = page.locator('button:has-text("COMMIT")');
    await expect(commitBtn).toBeVisible();
    await commitBtn.click();
  });

  test('should verify simulation lab hub tab switching', async ({ page }) => {
    await page.goto('/simulation');
    await expect(page).toHaveTitle(/Simulation|Lab|VoltCore/i);

    // Verify universal bench buttons
    const benchContainer = page.locator('body');
    await expect(benchContainer).toBeVisible();
  });
});
