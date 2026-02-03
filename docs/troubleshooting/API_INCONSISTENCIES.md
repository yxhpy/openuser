# API Inconsistencies Analysis

**Date**: 2026-02-03
**Status**: Identified

## Overview

This document identifies inconsistencies between frontend TypeScript types and backend Pydantic schemas that may cause runtime errors.

## Critical Inconsistencies

### 1. Authentication API

#### TokenResponse Mismatch
**Backend** (`src/api/schemas.py:107-114`):
```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # REQUIRED field
    user: Optional[UserResponse] = None
```

**Frontend** (`frontend/src/types/auth.ts:21-26`):
```typescript
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;  // Missing: expires_in field
}
```

**Impact**: Frontend doesn't handle `expires_in`, may cause token refresh issues.

---

### 2. Digital Human API

#### CreateDigitalHumanRequest Mismatch
**Backend** (`src/api/schemas.py:139-145`):
```python
class DigitalHumanCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    voice_model_path: Optional[str] = None  # Backend accepts this
```

**Frontend** (`frontend/src/types/digitalHuman.ts:16-20`):
```typescript
export interface CreateDigitalHumanRequest {
  name: string;
  description?: string;
  image?: File;  // Frontend sends image, backend doesn't define it in schema
}
```

**Impact**:
- Frontend sends `image` as File, but backend schema doesn't define it
- Backend accepts `voice_model_path`, but frontend doesn't send it
- May cause validation errors or missing functionality

---

#### GenerateVideoRequest Mismatch
**Backend** (`src/api/schemas.py:172-186`):
```python
class VideoGenerateRequest(BaseModel):
    digital_human_id: int
    text: Optional[str] = None
    mode: str = "enhanced_talking_head"
    # No audio or speaker_wav fields defined
```

**Frontend** (`frontend/src/types/digitalHuman.ts:22-28`):
```typescript
export interface GenerateVideoRequest {
  digital_human_id: number;
  text?: string;
  audio?: File;  // Not in backend schema
  mode: 'lipsync' | 'talking_head' | 'enhanced_lipsync' | 'enhanced_talking_head';
  speaker_wav?: string;  // Not in backend schema
}
```

**Impact**: Frontend sends `audio` and `speaker_wav`, but backend schema doesn't validate them. May cause silent failures.

---

#### VideoGenerateResponse Mismatch
**Backend** (`src/api/schemas.py:189-195`):
```python
class VideoGenerateResponse(BaseModel):
    video_path: str
    digital_human_id: int
    mode: str
    message: str
```

**Frontend** (`frontend/src/types/digitalHuman.ts:30-33`):
```typescript
export interface GenerateVideoResponse {
  video_path: string;
  message: string;
  // Missing: digital_human_id, mode
}
```

**Impact**: Frontend doesn't expect `digital_human_id` and `mode` in response, may cause type errors.

---

### 3. User Schema Mismatch

**Backend** (`src/api/schemas.py:123-134`):
```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool  # REQUIRED
    is_superuser: bool  # REQUIRED
    created_at: str  # REQUIRED
```

**Frontend** (`frontend/src/types/auth.ts:1-8`):
```typescript
export interface User {
  id: number;
  username: string;
  email: string;
  is_active?: boolean;  // Optional in frontend
  is_superuser?: boolean;  // Optional in frontend
  created_at?: string;  // Optional in frontend
}
```

**Impact**: Frontend treats required fields as optional, may cause undefined errors.

---

## Summary of Issues

| API Endpoint | Issue | Severity |
|--------------|-------|----------|
| `/api/v1/auth/login` | Missing `expires_in` in frontend | High |
| `/api/v1/auth/register` | Missing `expires_in` in frontend | High |
| `/api/v1/digital-human/create` | `image` not in backend schema | High |
| `/api/v1/digital-human/generate` | `audio`, `speaker_wav` not in backend schema | High |
| `/api/v1/digital-human/generate` | Response fields mismatch | Medium |
| User type | Required fields marked as optional | Medium |

## Recommended Actions

1. **Immediate**: Fix critical type mismatches
2. **Short-term**: Generate TypeScript types from Pydantic schemas automatically
3. **Long-term**: Implement API contract testing to catch these issues early

## Next Steps

- [ ] Update backend schemas to match actual API behavior
- [ ] Update frontend types to match backend schemas
- [ ] Add type generation script
- [ ] Add API contract tests
- [ ] Add E2E tests to validate integration
