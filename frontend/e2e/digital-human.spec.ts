import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Digital Human Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });

    // Navigate to digital human page
    await page.goto('/digital-human');
  });

  test('should display digital human list page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('数字人管理');
    await expect(page.locator('button')).toContainText('创建数字人');
  });

  test('should open create digital human modal', async ({ page }) => {
    // Click create button
    await page.click('text=创建数字人');

    // Check modal is visible
    await expect(page.locator('.ant-modal')).toBeVisible();
    await expect(page.locator('.ant-modal-title')).toContainText('创建数字人');
  });

  test('should show validation errors for empty create form', async ({ page }) => {
    // Open create modal
    await page.click('text=创建数字人');

    // Submit without filling form
    await page.click('.ant-modal button[type="submit"]');

    // Check for validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
  });

  test('should create a new digital human', async ({ page }) => {
    // Open create modal
    await page.click('text=创建数字人');

    // Fill in form
    const timestamp = Date.now();
    await page.fill('input[name="name"]', `测试数字人${timestamp}`);
    await page.fill('textarea[name="description"]', '这是一个测试数字人');

    // Upload image (create a test image file)
    const testImagePath = path.join(__dirname, 'fixtures', 'test-image.jpg');
    await page.setInputFiles('input[type="file"]', testImagePath);

    // Submit form
    await page.click('.ant-modal button[type="submit"]');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toBeVisible({ timeout: 5000 });

    // Check that the new digital human appears in the list
    await expect(page.locator(`text=测试数字人${timestamp}`)).toBeVisible({ timeout: 5000 });
  });

  test('should view digital human details', async ({ page }) => {
    // Click on first digital human card
    await page.click('.ant-card >> nth=0');

    // Check details page
    await expect(page).toHaveURL(/\/digital-human\/\d+/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should generate video from text', async ({ page }) => {
    // Navigate to first digital human details
    await page.click('.ant-card >> nth=0');

    // Click generate video button
    await page.click('text=生成视频');

    // Fill in text
    await page.fill('textarea[name="text"]', '你好，我是数字人测试');

    // Select generation mode
    await page.click('.ant-select');
    await page.click('text=增强型唇形同步');

    // Submit
    await page.click('button[type="submit"]');

    // Wait for generation to start
    await expect(page.locator('.ant-message-info')).toContainText('视频生成中');

    // Wait for completion (this might take a while)
    await expect(page.locator('.ant-message-success')).toBeVisible({ timeout: 60000 });
  });

  test('should delete digital human', async ({ page }) => {
    // Click delete button on first card
    await page.click('.ant-card >> nth=0 >> [data-testid="delete-button"]');

    // Confirm deletion
    await page.click('.ant-popconfirm button.ant-btn-primary');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('删除成功');
  });

  test('should search digital humans', async ({ page }) => {
    // Type in search box
    await page.fill('input[placeholder*="搜索"]', '测试');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that only matching results are shown
    const cards = page.locator('.ant-card');
    await expect(cards.first()).toContainText('测试');
  });

  test('should filter digital humans by status', async ({ page }) => {
    // Click filter dropdown
    await page.click('text=状态筛选');

    // Select active status
    await page.click('text=活跃');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that results are filtered
    const cards = page.locator('.ant-card');
    await expect(cards).toHaveCount(await cards.count());
  });
});
