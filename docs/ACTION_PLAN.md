# Action Plan - Frontend Testing & API Fixes

**Status**: 🟡 In Progress
**Priority**: High
**Estimated Effort**: 2-3 days

## Completed ✅

1. ✅ **Analyzed API inconsistencies** - 6 critical issues documented
2. ✅ **Setup frontend testing framework** - Vitest + RTL + MSW configured
3. ✅ **Generated TypeScript types** - 30 interfaces auto-generated from Pydantic schemas
4. ✅ **Created documentation** - Testing guide, API analysis, upgrade summary

## Remaining Tasks 📝

### Task #4: Write Frontend Unit Tests (Priority: High)

**Components to test**:
- [ ] `LoginPage.tsx` - Login form, validation, error handling
- [ ] `RegisterPage.tsx` - Registration form, password validation
- [ ] `DashboardPage.tsx` - Dashboard layout, data display
- [ ] `CreatePage.tsx` - Digital human creation form
- [ ] `ListPage.tsx` - Digital human list, pagination
- [ ] `DetailPage.tsx` - Digital human details, actions
- [ ] `GenerateVideoPage.tsx` - Video generation form
- [ ] `ProtectedRoute.tsx` - Auth guard logic
- [ ] `AppLayout.tsx` - Layout component

**API clients to test**:
- [x] `auth.ts` - Sample test created
- [ ] `digitalHuman.ts` - CRUD operations
- [ ] `client.ts` - Axios interceptors, error handling

**Target**: 80% coverage

**Example command**:
```bash
cd frontend
npm test -- src/pages/auth/LoginPage.test.tsx
```

---

### Task #5: Write E2E Tests (Priority: Medium)

**Setup**:
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

**Critical flows to test**:
- [ ] User registration flow
- [ ] User login flow
- [ ] Create digital human
- [ ] Upload image
- [ ] Generate video
- [ ] View digital human list
- [ ] Delete digital human

**Example test**:
```typescript
test('user can login and create digital human', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.fill('[name="username"]', 'testuser');
  await page.fill('[name="password"]', 'Test123!');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
  // ... continue flow
});
```

---

### Task #6: Create API Contract Tests (Priority: High)

**Goal**: Ensure frontend API calls match backend expectations

**Approach**:
1. Use MSW handlers to validate request/response shapes
2. Add schema validation using Zod or similar
3. Test error responses

**Example**:
```typescript
describe('API Contract: Auth', () => {
  it('login request matches backend schema', async () => {
    const request = { username: 'test', password: 'Test123!' };
    // Validate request shape
    expect(request).toMatchSchema(LoginRequestSchema);

    const response = await authApi.login(request);
    // Validate response shape
    expect(response).toMatchSchema(AuthResponseSchema);
  });
});
```

---

## Critical API Fixes Required 🔧

### Fix #1: Update Backend Schemas

**File**: `src/api/schemas.py`

```python
# Add image field to DigitalHumanCreateRequest
class DigitalHumanCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    voice_model_path: Optional[str] = None
    image: Optional[UploadFile] = None  # ADD THIS

# Add audio fields to VideoGenerateRequest
class VideoGenerateRequest(BaseModel):
    digital_human_id: int
    text: Optional[str] = None
    mode: str = "enhanced_talking_head"
    audio: Optional[UploadFile] = None  # ADD THIS
    speaker_wav: Optional[str] = None   # ADD THIS
```

### Fix #2: Update Frontend Types

**File**: `frontend/src/types/auth.ts`

```typescript
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;  // ADD THIS
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;      // Make required
  is_superuser: boolean;   // Make required
  created_at: string;      // Make required
}
```

### Fix #3: Update Frontend API Calls

**File**: `frontend/src/api/auth.ts`

```typescript
// Store expires_in for token refresh logic
async login(data: LoginRequest): Promise<AuthResponse> {
  const response = await client.post<AuthResponse>('/api/v1/auth/login', data);

  // Store token expiration
  const expiresAt = Date.now() + (response.data.expires_in * 1000);
  localStorage.setItem('token_expires_at', expiresAt.toString());

  return response.data;
}
```

---

## Testing Workflow 🔄

### Daily Development

```bash
# 1. Start backend
source venv/bin/activate
uvicorn src.api.main:app --reload

# 2. Start frontend
cd frontend
npm run dev

# 3. Run tests in watch mode
npm test
```

### Before Committing

```bash
# 1. Regenerate types if schemas changed
python scripts/generate_types.py

# 2. Run all frontend tests
cd frontend
npm run test:run

# 3. Check coverage
npm run test:coverage

# 4. Run backend tests
pytest --cov --cov-fail-under=100

# 5. Lint
npm run lint
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov --cov-fail-under=100

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm run test:run
      - name: Check coverage
        run: cd frontend && npm run test:coverage
```

---

## Success Criteria ✨

- [ ] Frontend test coverage ≥ 80%
- [ ] All API inconsistencies fixed
- [ ] All critical user flows have E2E tests
- [ ] Type generation integrated into workflow
- [ ] CI/CD pipeline passing
- [ ] No runtime type errors in production

---

## Timeline

**Day 1**: Fix API inconsistencies, write component tests
**Day 2**: Write E2E tests, add contract tests
**Day 3**: Achieve coverage target, integrate CI/CD

---

## Resources

- **Testing Guide**: `docs/testing/FRONTEND_TESTING.md`
- **API Issues**: `docs/troubleshooting/API_INCONSISTENCIES.md`
- **Upgrade Summary**: `docs/UPGRADE_SUMMARY.md`
- **Type Generation**: `scripts/README.md`

---

## Questions?

1. Check documentation first
2. Review test examples in `frontend/src/api/__tests__/`
3. Check MSW handlers in `frontend/src/test/mocks/`
4. Open an issue if stuck
