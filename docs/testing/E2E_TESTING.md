# E2E Testing Guide

## Overview

OpenUser frontend uses Playwright for end-to-end testing. Playwright provides reliable, fast, and cross-browser testing capabilities.

## Installation

Playwright is already included in the project dependencies. To set up:

```bash
cd frontend
npm install
npx playwright install
```

## Test Structure

### Test Files

All E2E tests are located in `frontend/e2e/`:

- **auth.spec.ts** - Authentication flow tests (login, register, logout)
- **dashboard.spec.ts** - Dashboard and navigation tests
- **digital-human.spec.ts** - Digital human management tests
- **plugins.spec.ts** - Plugin management tests
- **scheduler.spec.ts** - Task scheduler tests

### Test Fixtures

Test fixtures (images, files, etc.) are stored in `frontend/e2e/fixtures/`:

- **test-image.jpg** - Test image for digital human creation

## Running Tests

### All Tests

```bash
# Run all tests in headless mode
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed
```

### Specific Tests

```bash
# Run specific test file
npx playwright test auth.spec.ts

# Run specific test by name
npx playwright test -g "should login successfully"

# Run tests in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Debugging

```bash
# Debug mode (step through tests)
npm run test:e2e:debug

# Debug specific test
npx playwright test auth.spec.ts --debug

# Generate test code
npx playwright codegen http://localhost:5173
```

### Reports

```bash
# View HTML report
npm run test:e2e:report

# View trace
npx playwright show-trace trace.zip
```

## Configuration

Playwright configuration is in `frontend/playwright.config.ts`:

```typescript
{
  testDir: './e2e',
  baseURL: 'http://localhost:5173',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
}
```

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await page.click('button');
    await expect(page.locator('h1')).toContainText('Expected Text');
  });
});
```

### Best Practices

1. **Use data-testid attributes** for stable selectors:
   ```typescript
   await page.click('[data-testid="submit-button"]');
   ```

2. **Wait for elements properly**:
   ```typescript
   // Good
   await expect(page.locator('.message')).toBeVisible();

   // Avoid
   await page.waitForTimeout(1000);
   ```

3. **Use unique test data**:
   ```typescript
   const timestamp = Date.now();
   const username = `testuser${timestamp}`;
   ```

4. **Clean up after tests**:
   ```typescript
   test.afterEach(async ({ page }) => {
    // Clean up test data
   });
   ```

5. **Test critical user flows**:
   - Focus on end-to-end user journeys
   - Test happy paths and error cases
   - Verify UI feedback and error messages

## Test Coverage

### Authentication Flow
- ✅ Login with valid/invalid credentials
- ✅ Registration with validation
- ✅ Password mismatch handling
- ✅ Logout functionality

### Dashboard
- ✅ Display statistics
- ✅ Navigation between pages
- ✅ Quick actions
- ✅ User menu and settings
- ✅ Notifications
- ✅ Global search

### Digital Human Management
- ✅ List digital humans
- ✅ Create new digital human
- ✅ Upload image
- ✅ Generate video from text
- ✅ Delete digital human
- ✅ Search and filter

### Plugin Management
- ✅ List plugins
- ✅ Install new plugin
- ✅ Reload plugin
- ✅ Enable/disable plugin
- ✅ View plugin details
- ✅ Uninstall plugin

### Task Scheduler
- ✅ List tasks
- ✅ Create scheduled task
- ✅ Edit task
- ✅ Pause/resume task
- ✅ Run task manually
- ✅ Delete task
- ✅ Validate cron expression
- ✅ View execution history

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Troubleshooting

### Common Issues

1. **"Target closed" error**
   - Increase timeout in config
   - Check if dev server is running
   - Verify no port conflicts

2. **"Timeout waiting for element"**
   - Verify selector is correct
   - Check if element is visible
   - Add proper waits

3. **Flaky tests**
   - Avoid `waitForTimeout()`
   - Use `await expect()` for waits
   - Check for race conditions
   - Increase retries in CI

4. **Browser not found**
   - Run `npx playwright install`
   - Check Playwright version

### Debug Tips

1. **Use UI mode** for visual debugging:
   ```bash
   npm run test:e2e:ui
   ```

2. **Add console logs**:
   ```typescript
   console.log(await page.content());
   ```

3. **Take screenshots**:
   ```typescript
   await page.screenshot({ path: 'debug.png' });
   ```

4. **Pause execution**:
   ```typescript
   await page.pause();
   ```

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [CI/CD Integration](https://playwright.dev/docs/ci)

## Next Steps

1. Add more test scenarios for edge cases
2. Implement page object pattern for complex pages
3. Add visual regression testing
4. Set up CI/CD pipeline
5. Add performance testing with Playwright
6. Implement API mocking for isolated tests
