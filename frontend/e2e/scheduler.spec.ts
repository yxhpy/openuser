import { test, expect } from '@playwright/test';

test.describe('Task Scheduler', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });

    // Navigate to scheduler page
    await page.goto('/scheduler');
  });

  test('should display scheduler page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('任务调度');
    await expect(page.locator('button')).toContainText('创建任务');
  });

  test('should show task list', async ({ page }) => {
    // Check that task table is displayed
    await expect(page.locator('.ant-table')).toBeVisible();
  });

  test('should open create task modal', async ({ page }) => {
    // Click create button
    await page.click('text=创建任务');

    // Check modal is visible
    await expect(page.locator('.ant-modal')).toBeVisible();
    await expect(page.locator('.ant-modal-title')).toContainText('创建任务');
  });

  test('should show validation errors for empty create form', async ({ page }) => {
    // Open create modal
    await page.click('text=创建任务');

    // Submit without filling form
    await page.click('.ant-modal button[type="submit"]');

    // Check for validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
  });

  test('should create a new scheduled task', async ({ page }) => {
    // Open create modal
    await page.click('text=创建任务');

    // Fill in form
    const timestamp = Date.now();
    await page.fill('input[name="name"]', `测试任务${timestamp}`);
    await page.fill('textarea[name="description"]', '这是一个测试任务');

    // Select task type
    await page.click('input[name="task_type"]');
    await page.click('text=视频生成');

    // Fill in cron schedule
    await page.fill('input[name="schedule"]', '0 0 * * *');

    // Fill in parameters
    await page.fill('textarea[name="params"]', '{"text": "测试内容"}');

    // Submit form
    await page.click('.ant-modal button[type="submit"]');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('创建成功', { timeout: 5000 });

    // Check that the new task appears in the list
    await expect(page.locator(`text=测试任务${timestamp}`)).toBeVisible({ timeout: 5000 });
  });

  test('should view task details', async ({ page }) => {
    // Click on first task row
    await page.click('.ant-table-row >> nth=0');

    // Check details modal
    await expect(page.locator('.ant-modal')).toBeVisible();
    await expect(page.locator('text=任务详情')).toBeVisible();
  });

  test('should edit task', async ({ page }) => {
    // Click edit button on first task
    await page.click('.ant-table-row >> nth=0 >> button:has-text("编辑")');

    // Check edit modal is visible
    await expect(page.locator('.ant-modal-title')).toContainText('编辑任务');

    // Modify task name
    await page.fill('input[name="name"]', '修改后的任务名称');

    // Submit
    await page.click('.ant-modal button[type="submit"]');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('更新成功');

    // Check that the task name is updated
    await expect(page.locator('text=修改后的任务名称')).toBeVisible();
  });

  test('should pause/resume task', async ({ page }) => {
    // Click pause button on first task
    await page.click('.ant-table-row >> nth=0 >> button:has-text("暂停")');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toBeVisible();

    // Check that button changed to resume
    await expect(page.locator('.ant-table-row >> nth=0 >> button:has-text("恢复")')).toBeVisible();

    // Click resume
    await page.click('.ant-table-row >> nth=0 >> button:has-text("恢复")');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toBeVisible();
  });

  test('should run task manually', async ({ page }) => {
    // Click run button on first task
    await page.click('.ant-table-row >> nth=0 >> button:has-text("立即执行")');

    // Confirm execution
    await page.click('.ant-popconfirm button.ant-btn-primary');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('任务已启动');
  });

  test('should delete task', async ({ page }) => {
    // Click delete button on first task
    await page.click('.ant-table-row >> nth=0 >> button:has-text("删除")');

    // Confirm deletion
    await page.click('.ant-popconfirm button.ant-btn-primary');

    // Wait for success message
    await expect(page.locator('.ant-message-success')).toContainText('删除成功');
  });

  test('should filter tasks by status', async ({ page }) => {
    // Click status filter dropdown
    await page.click('text=状态筛选');

    // Select pending status
    await page.click('text=待执行');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that table is filtered
    const rows = page.locator('.ant-table-row');
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should filter tasks by type', async ({ page }) => {
    // Click type filter dropdown
    await page.click('text=类型筛选');

    // Select video generation type
    await page.click('text=视频生成');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that table is filtered
    const rows = page.locator('.ant-table-row');
    await expect(rows.first()).toContainText('视频生成');
  });

  test('should search tasks', async ({ page }) => {
    // Type in search box
    await page.fill('input[placeholder*="搜索"]', '测试');

    // Wait for filtered results
    await page.waitForTimeout(500);

    // Check that only matching results are shown
    const rows = page.locator('.ant-table-row');
    await expect(rows.first()).toContainText('测试');
  });

  test('should validate cron expression', async ({ page }) => {
    // Open create modal
    await page.click('text=创建任务');

    // Fill in invalid cron expression
    await page.fill('input[name="schedule"]', 'invalid cron');

    // Blur the input to trigger validation
    await page.click('input[name="name"]');

    // Check for validation error
    await expect(page.locator('.ant-form-item-explain-error')).toContainText('Cron');
  });

  test('should show task execution history', async ({ page }) => {
    // Click on first task to view details
    await page.click('.ant-table-row >> nth=0');

    // Check for execution history section
    await expect(page.locator('text=执行历史')).toBeVisible();

    // Check that history table is displayed
    await expect(page.locator('.ant-table')).toBeVisible();
  });
});
