# E2E Tests with Playwright

This directory contains end-to-end tests for the OpenUser frontend application using Playwright.

## Setup

Playwright is already installed as a dev dependency. To install browsers:

```bash
npx playwright install
```

## Running Tests

### Run all tests (headless)
```bash
npm run test:e2e
```

### Run tests with UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Debug tests
```bash
npm run test:e2e:debug
```

### View test report
```bash
npm run test:e2e:report
```

### Run specific test file
```bash
npx playwright test auth.spec.ts
```

### Run tests in specific browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Structure

```
e2e/
├── auth.spec.ts           # Authentication flow tests
├── dashboard.spec.ts      # Dashboard and navigation tests
├── digital-human.spec.ts  # Digital human management tests
├── plugins.spec.ts        # Plugin management tests
├── scheduler.spec.ts      # Task scheduler tests
├── fixtures/              # Test fixtures (images, files, etc.)
│   └── test-image.jpg    # Test image for digital human creation
└── generate-test-image.py # Script to generate test image
```

## Test Coverage

### Authentication (auth.spec.ts)
- Display login page
- Form validation
- Invalid credentials error
- Navigate to register page
- Register form validation
- Password mismatch validation
- Successful registration and login
- Logout functionality

### Dashboard (dashboard.spec.ts)
- Display dashboard after login
- Show user information
- Display statistics cards
- Navigation to different pages
- Recent activities
- Quick actions
- Sidebar toggle
- User dropdown menu
- Breadcrumb navigation
- Notifications
- Global search
- 404 page handling

### Digital Human (digital-human.spec.ts)
- Display digital human list
- Create digital human modal
- Form validation
- Create new digital human
- View digital human details
- Generate video from text
- Delete digital human
- Search digital humans
- Filter by status

### Plugins (plugins.spec.ts)
- Display plugins list
- Show plugin cards
- Install plugin modal
- Form validation
- Install new plugin
- Reload plugin
- View plugin details
- Enable/disable plugin
- Search plugins
- Filter by status
- Show plugin dependencies
- Uninstall plugin

### Scheduler (scheduler.spec.ts)
- Display scheduler page
- Show task list
- Create task modal
- Form validation
- Create new scheduled task
- View task details
- Edit task
- Pause/resume task
- Run task manually
- Delete task
- Filter by status and type
- Search tasks
- Validate cron expression
- Show execution history

## Configuration

The Playwright configuration is in `playwright.config.ts`. Key settings:

- **Base URL**: `http://localhost:5173` (Vite dev server)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Retries**: 2 on CI, 0 locally
- **Trace**: On first retry
- **Screenshot**: On failure
- **Video**: Retain on failure
- **Web Server**: Automatically starts Vite dev server before tests

## Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Wait for elements** using `await expect()` instead of `waitForTimeout()`
3. **Use page object pattern** for complex pages
4. **Mock API responses** when testing UI logic
5. **Clean up test data** after each test
6. **Use unique identifiers** (timestamps) for test data
7. **Test critical user flows** end-to-end
8. **Keep tests independent** - each test should work in isolation

## Debugging

### Visual debugging with UI mode
```bash
npm run test:e2e:ui
```

### Debug specific test
```bash
npx playwright test auth.spec.ts --debug
```

### View trace
```bash
npx playwright show-trace trace.zip
```

### Generate test code
```bash
npx playwright codegen http://localhost:5173
```

## CI/CD Integration

Tests are configured to run in CI with:
- Parallel execution disabled (`workers: 1`)
- 2 retries for flaky tests
- HTML report generation
- Trace collection on failures

## Troubleshooting

### Tests fail with "Target closed"
- Increase timeout in `playwright.config.ts`
- Check if dev server is running properly

### Tests fail with "Timeout waiting for element"
- Check if element selector is correct
- Verify element is visible and not hidden
- Increase timeout if needed

### Tests fail intermittently
- Add proper waits using `await expect()`
- Avoid using `waitForTimeout()` for synchronization
- Check for race conditions

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
