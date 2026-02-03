# Scripts

This directory contains utility scripts for the OpenUser project.

## generate_types.py

Automatically generates TypeScript types from backend Pydantic schemas.

### Usage

```bash
python scripts/generate_types.py
```

### What it does

1. Reads Pydantic models from `src/api/schemas.py`
2. Converts Python type annotations to TypeScript types
3. Generates TypeScript interfaces in `frontend/src/types/generated.ts`

### Type Mapping

| Python Type | TypeScript Type |
|-------------|-----------------|
| `str` | `string` |
| `int` | `number` |
| `float` | `number` |
| `bool` | `boolean` |
| `datetime` | `string` (ISO 8601) |
| `Optional[T]` | `T \| null` |
| `List[T]` | `T[]` |
| `Dict[K, V]` | `Record<K, V>` |

### When to run

- After modifying `src/api/schemas.py`
- Before committing changes to API schemas
- When frontend types are out of sync with backend

### Automation

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Regenerate TypeScript types if schemas changed
if git diff --cached --name-only | grep -q "src/api/schemas.py"; then
    echo "Regenerating TypeScript types..."
    python scripts/generate_types.py
    git add frontend/src/types/generated.ts
fi
```

## Future Scripts

- `validate_api_contracts.py` - Validate frontend-backend API contracts
- `generate_api_docs.py` - Generate API documentation
- `check_coverage.py` - Check test coverage thresholds
