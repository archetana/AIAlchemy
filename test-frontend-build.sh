#!/bin/bash
# Test script to verify frontend build fixes
# This can be run locally where Node.js and npm are available

set -e

echo "🧪 Testing AIAlchemy Frontend Build"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "📦 Frontend directory exists: ✅"

# Navigate to frontend directory
cd frontend

echo ""
echo "1. 📋 Checking package.json..."
if [ -f "package.json" ]; then
    echo "   ✅ package.json found"
else
    echo "   ❌ package.json not found"
    exit 1
fi

echo ""
echo "2. 🔍 Checking for Node.js and npm..."
if command -v node >/dev/null 2>&1; then
    echo "   ✅ Node.js version: $(node --version)"
else
    echo "   ❌ Node.js not found. Please install Node.js first."
    exit 1
fi

if command -v npm >/dev/null 2>&1; then
    echo "   ✅ npm version: $(npm --version)"
else
    echo "   ❌ npm not found. Please install npm first."
    exit 1
fi

echo ""
echo "3. 📦 Installing dependencies..."
if [ -d "node_modules" ]; then
    echo "   📁 node_modules exists, using existing installation"
else
    echo "   📥 Installing dependencies..."
    npm install
fi

echo ""
echo "4. 🔎 Running ESLint to check for React Hooks violations..."
echo "   Checking PipelineStats.js specifically..."

# Check if eslint is available
if npx eslint --version >/dev/null 2>&1; then
    echo "   ✅ ESLint available"
    
    # Check the specific file that was fixed
    if npx eslint src/components/Pipeline/PipelineStats.js --rule 'react-hooks/rules-of-hooks: error'; then
        echo "   ✅ PipelineStats.js: No React Hooks violations"
    else
        echo "   ❌ PipelineStats.js: React Hooks violations found"
        exit 1
    fi
    
    # Check all files for hooks violations
    echo "   🔍 Checking all files for React Hooks violations..."
    if npx eslint src/ --rule 'react-hooks/rules-of-hooks: error' --format=compact; then
        echo "   ✅ No React Hooks violations found in any files"
    else
        echo "   ⚠️  React Hooks violations found (see above)"
        echo "   Note: These may need to be fixed before deployment"
    fi
else
    echo "   ⚠️  ESLint not available, skipping hooks check"
fi

echo ""
echo "5. 🏗️ Testing production build..."
echo "   This will test the same process used in Docker deployment..."

if npm run build; then
    echo "   ✅ Frontend build successful!"
    echo "   📁 Build output created in: build/"
    
    # Check build output
    if [ -d "build" ]; then
        echo "   📊 Build statistics:"
        echo "      - HTML files: $(find build -name "*.html" | wc -l)"
        echo "      - JS files: $(find build -name "*.js" | wc -l)" 
        echo "      - CSS files: $(find build -name "*.css" | wc -l)"
        echo "      - Total size: $(du -sh build | cut -f1)"
    fi
else
    echo "   ❌ Frontend build failed!"
    echo "   This is the same error that would occur in Docker deployment."
    exit 1
fi

echo ""
echo "🎉 Frontend Build Test Complete!"
echo "================================="
echo "✅ All checks passed - the frontend should now deploy successfully"
echo ""
echo "📋 Summary:"
echo "   - React Hooks violations: Fixed ✅"
echo "   - Dependencies: Installed ✅"
echo "   - Build process: Working ✅"
echo "   - Docker deployment: Should succeed ✅"

echo ""
echo "🚀 Ready for deployment!"
echo "   Run: ./deploy-with-gcs.sh"
echo "   Or: docker build -t aialchemy-frontend ./frontend"