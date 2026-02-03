# Frontend Testing Guide

## Overview

This guide covers the frontend testing setup for the OpenUser project, including unit tests, integration tests, and E2E tests.

## Testing Stack

- **Test Runner**: Vitest
- **Component Testing**: React Testing Library
- **API Mocking**: MSW (Mock Service Worker)
- **E2E Testing**: Playwright (to be added)
- **Coverage**: Vitest Coverage (v8)

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── __tests__/          # API client tests
│   │   │   └── auth.test.ts
│   │   ├── auth.ts
│   │   └── digitalHuman.ts
│   ├── components/
│   │   └── __tests__/          # Component tests
│   ├── pages/
│   │   └── __tests__/          # Page tests
│   ├── test/
│   │   ├── mocks/
│   │   │   ├── handlers.ts     # MSW request handlers
│   │   │   └── server.ts       # MSW server setup
│   │   ├── setup.ts            # Test setup
│   │   └── utils.tsx           # Test utilities
│   └── types/
├── vitest.config.ts            # Vitest configuration
└── package.json
```

## Running Tests

```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Coverage Requirements

- **Lines**: 80%
- **Functions**: 80%
- **Branches**: 80%
- **Statements**: 80%

## Writing Tests

### Unit Tests for API Clients

```typescript
import { describe, it, expect, vi } from 'vitest';
import { authApi } from '@/api/auth';

describe('Auth API', () => {
  it('should login successfully', async () => {
    const result = await authApi.login({
      username: 'testuser',
      password: 'Test123!',
    });

    expect(result.access_token).toBeDefined();
    expect(result.user.username).toBe('testuser');
  });
});
```

### Component Tests

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/utils';
import { LoginPage } from '@/pages/auth/LoginPage';

describe('LoginPage', () => {
  it('should render login form', () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
});
```

### Integration Tests with MSW

MSW (Mock Service Worker) intercepts network requests and provides mock responses:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '@/pages/auth/LoginPage';

describe('LoginPage Integration', () => {
  it('should login successfully', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/password/i), 'Test123!');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    });
  });
});
```

## API Mocking with MSW

### Adding New Mock Handlers

Edit `src/test/mocks/handlers.ts`:

```typescript
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/your-endpoint', () => {
    return HttpResponse.json({ data: 'mock data' });
  }),
];
```

### Overriding Handlers in Tests

```typescript
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';

it('should handle error', async () => {
  server.use(
    http.get('/api/v1/endpoint', () => {
      return HttpResponse.json(
        { error: 'Something went wrong' },
        { status: 500 }
      );
    })
  );

  // Your test code
});
```

## Best Practices

### 1. Test User Behavior, Not Implementation

❌ Bad:
```typescript
expect(component.state.isLoading).toBe(true);
```

✅ Good:
```typescript
expect(screen.getByRole('progressbar')).toBeInTheDocument();
```

### 2. Use Semantic Queries

Prefer queries in this order:
1. `getByRole` - Most accessible
2. `getByLabelText` - For form fields
3. `getByPlaceholderText` - For inputs
4. `getByText` - For non-interactive elements
5. `getByTestId` - Last resort

### 3. Wait for Async Updates

```typescript
await waitFor(() => {
  expect(screen.getByText(/success/i)).toBeInTheDocument();
});
```

### 4. Clean Up Side Effects

```typescript
afterEach(() => {
  vi.clearAllMocks();
  cleanup();
});
```

### 5. Test Error States

```typescript
it('should display error message on failure', async () => {
  server.use(
    http.post('/api/v1/auth/login', () => {
      return HttpResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    })
  );

  // Test error handling
});
```

## Common Patterns

### Testing Forms

```typescript
it('should submit form with valid data', async () => {
  const user = userEvent.setup();
  render(<MyForm />);

  await user.type(screen.getByLabelText(/name/i), 'John Doe');
  await user.type(screen.getByLabelText(/email/i), 'john@example.com');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  await waitFor(() => {
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});
```

### Testing Navigation

```typescript
it('should navigate to dashboard after login', async () => {
  const user = userEvent.setup();
  render(<LoginPage />);

  // Login
  await user.type(screen.getByLabelText(/username/i), 'testuser');
  await user.type(screen.getByLabelText(/password/i), 'Test123!');
  await user.click(screen.getByRole('button', { name: /login/i }));

  // Check navigation
  await waitFor(() => {
    expect(window.location.pathname).toBe('/dashboard');
  });
});
```

### Testing File Uploads

```typescript
it('should upload image', async () => {
  const user = userEvent.setup();
  const file = new File(['hello'], 'hello.png', { type: 'image/png' });

  render(<ImageUpload />);

  const input = screen.getByLabelText(/upload/i);
  await user.upload(input, file);

  await waitFor(() => {
    expect(screen.getByText(/hello.png/i)).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Issue: Tests timeout

**Solution**: Increase timeout in vitest.config.ts:

```typescript
export default defineConfig({
  test: {
    testTimeout: 10000,
  },
});
```

### Issue: MSW not intercepting requests

**Solution**: Ensure MSW server is started in setup.ts and check the API base URL matches.

### Issue: Component not rendering

**Solution**: Check if you're using `renderWithRouter` for components that use React Router.

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run frontend tests
  run: |
    cd frontend
    npm install
    npm run test:run
    npm run test:coverage
```

## Next Steps

1. Write tests for all existing components
2. Add E2E tests with Playwright
3. Integrate with CI/CD pipeline
4. Monitor coverage and maintain 80%+ threshold
