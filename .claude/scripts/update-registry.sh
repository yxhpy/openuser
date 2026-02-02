#!/bin/bash
# Update module registry by scanning source code
# Usage: ./update-registry.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY_FILE="$PROJECT_ROOT/docs/modules/REGISTRY.md"

echo "📝 Updating module registry..."
echo ""

# Backup existing registry
if [ -f "$REGISTRY_FILE" ]; then
    cp "$REGISTRY_FILE" "$REGISTRY_FILE.backup"
    echo "✅ Backed up existing registry to REGISTRY.md.backup"
fi

# Note: The actual registry update is done by the doc-agent
# This script is a placeholder that triggers the update process
echo "📊 Scanning source code in src/..."
echo ""

# Count Python files
PY_FILES=$(find "$PROJECT_ROOT/src" -name "*.py" -type f | wc -l | tr -d ' ')
echo "Found $PY_FILES Python files"

# Count test files
TEST_FILES=$(find "$PROJECT_ROOT/tests" -name "*.py" -type f | wc -l | tr -d ' ')
echo "Found $TEST_FILES test files"

echo ""
echo "💡 To update the registry, use the auto-doc skill or ask Claude to update it"
echo "   The doc-agent will scan the code and update docs/modules/REGISTRY.md"
echo ""
echo "✅ Registry update check complete"
