import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/OpenUser/);
    await expect(page.locator('h1')).toContainText('登录');
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    // Click login button without filling form
    await page.click('button[type="submit"]');

    // Check for validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[name="username"]', 'invaliduser');
    await page.fill('input[name="password"]', 'wrongpassword');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for error message
    await expect(page.locator('.ant-message-error')).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to register page', async ({ page }) => {
    // Click register link
    await page.click('text=立即注册');

    // Check URL and page content
    await expect(page).toHaveURL(/\/register/);
    await expect(page.locator('h1')).toContainText('注册');
  });

  test('should show validation errors for empty register form', async ({ page }) => {
    await page.goto('/register');

    // Click register button without filling form
    await page.click('button[type="submit"]');

    // Check for validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
  });

  test('should show error for password mismatch', async ({ page }) => {
    await page.goto('/register');

    // Fill in form with mismatched passwords
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'Password123!');
    await page.fill('input[name="confirmPassword"]', 'DifferentPassword123!');

    // Submit form
    await page.click('button[type="submit"]');

    // Check for validation error
    await expect(page.locator('.ant-form-item-explain-error')).toContainText('两次输入的密码不一致');
  });

  test('should successfully register and login', async ({ page }) => {
    // Generate unique username
    const timestamp = Date.now();
    const username = `testuser${timestamp}`;
    const email = `test${timestamp}@example.com`;
    const password = 'Password123!';

    // Navigate to register page
    await page.goto('/register');

    // Fill in registration form
    await page.fill('input[name="username"]', username);
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="confirmPassword"]', password);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for success message and redirect
    await expect(page.locator('.ant-message-success')).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });

    // Now login with the new account
    await page.fill('input[name="username"]', username);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 5000 });
  });

  test('should logout successfully', async ({ page }) => {
    // First login (assuming we have a test account)
    const username = 'testuser';
    const password = 'Password123!';

    await page.fill('input[name="username"]', username);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });

    // Click logout button (adjust selector based on your UI)
    await page.click('[data-testid="logout-button"]');

    // Should redirect to login page
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  });
});
