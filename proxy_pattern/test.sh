#!/bin/bash
# Quick test script for LiteLLM proxy
# Usage: bash test.sh

set -e

echo "🧪 LiteLLM Proxy Test Script"
echo "============================"
echo ""

# Get master key from .env or use default
if [ -f .env ]; then
    MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2)
    echo "✅ Using master key from .env"
else
    MASTER_KEY="sk-1234567890abcdef"
    echo "⚠️  Using default master key (no .env found)"
fi

echo "Master key: ${MASTER_KEY:0:20}..."
echo ""

# Check if proxy is running
echo "1️⃣  Checking proxy health..."
if curl -s -f http://localhost:4000/health > /dev/null 2>&1; then
    echo "✅ Proxy is healthy"
else
    echo "❌ Proxy is not responding"
    echo "   Run: docker compose up -d"
    exit 1
fi

echo ""
echo "2️⃣  Creating virtual key..."

# Create virtual key
RESPONSE=$(curl -s -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"max_budget": 10, "rpm_limit": 100}')

VIRTUAL_KEY=$(echo "$RESPONSE" | grep -o '"key":"[^"]*' | cut -d'"' -f4)

if [ -z "$VIRTUAL_KEY" ]; then
    echo "❌ Failed to create virtual key"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Virtual key created: ${VIRTUAL_KEY:0:20}..."
echo ""

echo "3️⃣  Making test request to gpt-5-nano..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer $VIRTUAL_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gpt-5-nano",
    "messages": [{"role": "user", "content": "Say hello in one word"}]
  }')

if echo "$CHAT_RESPONSE" | grep -q '"content"'; then
    CONTENT=$(echo "$CHAT_RESPONSE" | grep -o '"content":"[^"]*' | cut -d'"' -f4 | head -1)
    echo "✅ Response received: $CONTENT"
else
    echo "❌ Request failed"
    echo "Response: $CHAT_RESPONSE"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All tests passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Your virtual key: $VIRTUAL_KEY"
echo ""
echo "📋 Use this key for your application:"
echo "   curl -X POST http://localhost:4000/chat/completions \\"
echo "     -H 'Authorization: Bearer $VIRTUAL_KEY' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"model\":\"gpt-5-nano\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
