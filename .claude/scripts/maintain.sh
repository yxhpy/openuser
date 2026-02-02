#!/bin/bash
# Project maintenance script
# Usage: ./maintain.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔧 Running OpenUser project maintenance..."
echo ""

# 1. Update module registry
echo "📝 Step 1: Updating module registry..."
"$PROJECT_ROOT/.claude/scripts/update-registry.sh"
echo ""

# 2. Check test coverage
echo "🧪 Step 2: Checking test coverage..."
cd "$PROJECT_ROOT"
if [ -d "venv" ]; then
    source venv/bin/activate
fi

pytest --cov=src --cov-report=term-missing --tb=no -q 2>&1 | tail -20 || true
echo ""

# 3. Check for outdated dependencies
echo "📦 Step 3: Checking dependencies..."
if command -v pip-audit &> /dev/null; then
    pip-audit || echo "⚠️  Some vulnerabilities found (run 'pip-audit' for details)"
else
    echo "💡 Install pip-audit to check for vulnerabilities: pip install pip-audit"
fi
echo ""

# 4. Clean up temporary files
echo "🧹 Step 4: Cleaning up temporary files..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true
echo "✅ Cleaned up temporary files"
echo ""

# 5. Git status
echo "📊 Step 5: Git status..."
cd "$PROJECT_ROOT"
git status --short
echo ""

echo "✅ Maintenance complete!"
echo ""
echo "💡 Next steps:"
echo "   - Review test coverage and add missing tests"
echo "   - Update documentation if needed"
echo "   - Commit and push changes"
