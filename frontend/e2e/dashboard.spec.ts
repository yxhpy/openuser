import { test, expect } from '@playwright/test';

test.describe('Dashboard and Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });
  });

  test('should display dashboard after login', async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('h1')).toContainText('仪表盘');
  });

  test('should show user information', async ({ page }) => {
    // Check that user info is displayed
    await expect(page.locator('[data-testid="user-info"]')).toBeVisible();
    await expect(page.locator('text=testuser')).toBeVisible();
  });

  test('should display statistics cards', async ({ page }) => {
    // Check for statistics cards
    const cards = page.locator('.ant-statistic');
    await expect(cards).toHaveCount(4); // Assuming 4 stat cards

    // Check card titles
    await expect(page.locator('text=数字人总数')).toBeVisible();
    await expect(page.locator('text=任务总数')).toBeVisible();
    await expect(page.locator('text=插件总数')).toBeVisible();
    await expect(page.locator('text=今日生成')).toBeVisible();
  });

  test('should navigate to digital human page', async ({ page }) => {
    // Click digital human menu item
    await page.click('text=数字人管理');

    // Check URL
    await expect(page).toHaveURL(/\/digital-human/);
  });

  test('should navigate to plugins page', async ({ page }) => {
    // Click plugins menu item
    await page.click('text=插件管理');

    // Check URL
    await expect(page).toHaveURL(/\/plugins/);
  });

  test('should navigate to scheduler page', async ({ page }) => {
    // Click scheduler menu item
    await page.click('text=任务调度');

    // Check URL
    await expect(page).toHaveURL(/\/scheduler/);
  });

  test('should navigate to agents page', async ({ page }) => {
    // Click agents menu item
    await page.click('text=智能代理');

    // Check URL
    await expect(page).toHaveURL(/\/agents/);
  });

  test('should show recent activities', async ({ page }) => {
    // Check for recent activities section
    await expect(page.locator('text=最近活动')).toBeVisible();

    // Check that activity list is displayed
    await expect(page.locator('.ant-list')).toBeVisible();
  });

  test('should show quick actions', async ({ page }) => {
    // Check for quick actions section
    await expect(page.locator('text=快速操作')).toBeVisible();

    // Check quick action buttons
    await expect(page.locator('button:has-text("创建数字人")')).toBeVisible();
    await expect(page.locator('button:has-text("创建任务")')).toBeVisible();
  });

  test('should use quick action to create digital human', async ({ page }) => {
    // Click quick action button
    await page.click('button:has-text("创建数字人")');

    // Should navigate to digital human page with modal open
    await expect(page).toHaveURL(/\/digital-human/);
    await expect(page.locator('.ant-modal')).toBeVisible();
  });

  test('should toggle sidebar', async ({ page }) => {
    // Find sidebar toggle button
    const toggleButton = page.locator('[data-testid="sidebar-toggle"]');

    // Click to collapse
    await toggleButton.click();

    // Check sidebar is collapsed
    await expect(page.locator('.ant-layout-sider-collapsed')).toBeVisible();

    // Click to expand
    await toggleButton.click();

    // Check sidebar is expanded
    await expect(page.locator('.ant-layout-sider-collapsed')).not.toBeVisible();
  });

  test('should show user dropdown menu', async ({ page }) => {
    // Click user avatar/name
    await page.click('[data-testid="user-dropdown"]');

    // Check dropdown menu items
    await expect(page.locator('text=个人设置')).toBeVisible();
    await expect(page.locator('text=退出登录')).toBeVisible();
  });

  test('should navigate to settings', async ({ page }) => {
    // Click user dropdown
    await page.click('[data-testid="user-dropdown"]');

    // Click settings
    await page.click('text=个人设置');

    // Check URL
    await expect(page).toHaveURL(/\/settings/);
  });

  test('should handle breadcrumb navigation', async ({ page }) => {
    // Navigate to a nested page
    await page.goto('/digital-human/1');

    // Check breadcrumb
    await expect(page.locator('.ant-breadcrumb')).toBeVisible();
    await expect(page.locator('.ant-breadcrumb-link:has-text("首页")')).toBeVisible();
    await expect(page.locator('.ant-breadcrumb-link:has-text("数字人管理")')).toBeVisible();

    // Click breadcrumb to navigate back
    await page.click('.ant-breadcrumb-link:has-text("数字人管理")');

    // Check URL
    await expect(page).toHaveURL(/\/digital-human$/);
  });

  test('should show notifications', async ({ page }) => {
    // Click notification bell
    await page.click('[data-testid="notification-bell"]');

    // Check notification dropdown
    await expect(page.locator('.ant-dropdown')).toBeVisible();
    await expect(page.locator('text=通知')).toBeVisible();
  });

  test('should mark notification as read', async ({ page }) => {
    // Click notification bell
    await page.click('[data-testid="notification-bell"]');

    // Click first notification
    await page.click('.ant-list-item >> nth=0');

    // Check that notification is marked as read
    await expect(page.locator('.ant-list-item >> nth=0')).toHaveClass(/read/);
  });

  test('should search globally', async ({ page }) => {
    // Click search icon
    await page.click('[data-testid="global-search"]');

    // Type search query
    await page.fill('input[placeholder*="搜索"]', '测试');

    // Wait for search results
    await page.waitForTimeout(500);

    // Check search results dropdown
    await expect(page.locator('.ant-select-dropdown')).toBeVisible();
  });

  test('should handle 404 page', async ({ page }) => {
    // Navigate to non-existent page
    await page.goto('/non-existent-page');

    // Check 404 page
    await expect(page.locator('text=404')).toBeVisible();
    await expect(page.locator('text=页面不存在')).toBeVisible();

    // Click back to home button
    await page.click('button:has-text("返回首页")');

    // Should navigate to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
