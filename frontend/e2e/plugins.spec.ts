import { test, expect } from '@playwright/test';

test.describe('Plugin Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });

    // Navigate to plugins page
    await page.goto('/plugins');
  });

  test('should display plugins list page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('插件管理');
    await expect(page.locator('button')).toContainText('安装插件');
  });

  test('should show plugin cards with details', async ({ page }) => {
    // Check that plugin cards are displayed
    const cards = page.locator('.ant-card');
    await expect(cards.first()).toBeVisible();

    // Check card contains plugin information
    await expect(cards.first()).toContainText(/名称|版本|状态/);
  });

  test('should open install plugin modal', async ({ page }) => {
    // Click install button
    await page.click('text=安装插件');

    // Check modal is visible
    await expect(page.locator('.ant-modal')).toBeVisible();
    await expect(page.locator('.ant-modal-title')).toContainText('安装插件');
  });

  test('should show validation errors for empty install form', async ({ page }) => {
    // Open install modal
    await page.click('text=安装插件');

    // Submit without filling form
    await page.click('.ant-modal button[type="submit"]');

    // Check for validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
  });

  test('should install a new plugin', async ({ page }) => {
    // Open install modal
    await page.click('text=安装插件');

    // Fill in form
    await page.fill('input[name="name"]', 'test-plugin');
    await page.fill('input[name="version"]', '1.0.0');
    await page.fill('textarea[name="config"]', '{"enabled": true}');

    // Submit form
    await page.click('.ant-modal button[type="submit"]');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('安装成功', { timeout: 5000 });

    // Check that the new plugin appears in the list
    await expect(page.locator('text=test-plugin')).toBeVisible({ timeout: 5000 });
  });

  test('should reload a plugin', async ({ page }) => {
    // Find reload button on first plugin card
    await page.click('.ant-card >> nth=0 >> button:has-text("重载")');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('重载成功', { timeout: 5000 });
  });

  test('should view plugin details', async ({ page }) => {
    // Click on first plugin card
    await page.click('.ant-card >> nth=0');

    // Check details modal or page
    await expect(page.locator('.ant-modal, .plugin-details')).toBeVisible();
    await expect(page.locator('text=插件详情')).toBeVisible();
  });

  test('should enable/disable plugin', async ({ page }) => {
    // Find toggle switch on first plugin card
    const toggle = page.locator('.ant-card >> nth=0 >> .ant-switch');
    const initialState = await toggle.getAttribute('aria-checked');

    // Click toggle
    await toggle.click();

    // Wait for state change
    await page.waitForTimeout(500);

    // Check that state changed
    const newState = await toggle.getAttribute('aria-checked');
    expect(newState).not.toBe(initialState);

    // Check for success message
    await expect(page.locator('.ant-message-success')).toBeVisible();
  });

  test('should search plugins', async ({ page }) => {
    // Type in search box
    await page.fill('input[placeholder*="搜索"]', 'cache');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that only matching results are shown
    const cards = page.locator('.ant-card');
    await expect(cards.first()).toContainText('cache');
  });

  test('should filter plugins by status', async ({ page }) => {
    // Click filter dropdown
    await page.click('text=状态筛选');

    // Select loaded status
    await page.click('text=已加载');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that results are filtered
    const cards = page.locator('.ant-card');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should show plugin dependencies', async ({ page }) => {
    // Click on first plugin card to view details
    await page.click('.ant-card >> nth=0');

    // Check for dependencies section
    await expect(page.locator('text=依赖项')).toBeVisible();
  });

  test('should uninstall plugin', async ({ page }) => {
    // Click uninstall button on first card
    await page.click('.ant-card >> nth=0 >> button:has-text("卸载")');

    // Confirm uninstallation
    await page.click('.ant-popconfirm button.ant-btn-primary');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('卸载成功');
  });
});
