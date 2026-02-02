#!/bin/bash
# Search for existing features in the codebase
# Usage: ./search-feature.sh "keyword"

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <keyword>"
    echo "Example: $0 'voice synthesis'"
    exit 1
fi

KEYWORD="$1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔍 Searching for: $KEYWORD"
echo ""

# Search in module registry
echo "📦 Module Registry Matches:"
if grep -i "$KEYWORD" "$PROJECT_ROOT/docs/modules/REGISTRY.md" 2>/dev/null; then
    echo ""
else
    echo "  No matches found"
    echo ""
fi

# Search in API documentation
echo "🔌 API Documentation Matches:"
if grep -i "$KEYWORD" "$PROJECT_ROOT/docs/api/INDEX.md" 2>/dev/null; then
    echo ""
else
    echo "  No matches found"
    echo ""
fi

# Search in source code
echo "💻 Source Code Matches:"
if rg -i "$KEYWORD" "$PROJECT_ROOT/src/" --type py -l 2>/dev/null | head -10; then
    echo ""
else
    echo "  No matches found"
    echo ""
fi

# Search in tests
echo "🧪 Test Matches:"
if rg -i "$KEYWORD" "$PROJECT_ROOT/tests/" --type py -l 2>/dev/null | head -10; then
    echo ""
else
    echo "  No matches found"
    echo ""
fi

# Search in TODO
echo "📝 TODO Matches:"
if grep -i "$KEYWORD" "$PROJECT_ROOT/TODO.md" 2>/dev/null; then
    echo ""
else
    echo "  No matches found"
    echo ""
fi

echo "✅ Search complete"
