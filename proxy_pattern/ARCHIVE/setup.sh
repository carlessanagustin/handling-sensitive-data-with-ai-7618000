#!/bin/bash
# Simple setup script for LiteLLM proxy
# Usage: export OPENAI_API_KEY=sk-... && bash setup.sh

set -e

echo "🚀 LiteLLM Proxy - Setup"
echo "========================"
echo ""

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not found in environment"
    echo ""
    echo "Please export your OpenAI API key first:"
    echo "  export OPENAI_API_KEY=sk-your-key-here"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Please set OPENAI_API_KEY and try again."
        exit 1
    fi
else
    echo "✅ OPENAI_API_KEY found: ${OPENAI_API_KEY:0:20}..."
fi

echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✅ .env file found"
    
    # Update OPENAI_API_KEY in existing .env if provided
    if [ ! -z "$OPENAI_API_KEY" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
        else
            sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
        fi
        echo "✅ Updated OPENAI_API_KEY in .env"
    fi
else
    echo "📝 Creating .env from template..."
    cp .env.template .env
    echo "✅ Created .env file"
    echo ""
    echo "🔐 Generating secure keys..."
    
    # Generate keys
    MASTER_KEY="sk-$(openssl rand -hex 32)"
    SALT_KEY=$(openssl rand -base64 32)
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    
    # Update .env (macOS and Linux compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$MASTER_KEY/" .env
        sed -i '' "s/LITELLM_SALT_KEY=.*/LITELLM_SALT_KEY=$SALT_KEY/" .env
        sed -i '' "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
        sed -i '' "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
        
        # Add OPENAI_API_KEY if provided
        if [ ! -z "$OPENAI_API_KEY" ]; then
            sed -i '' "s|# OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
        fi
    else
        sed -i "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$MASTER_KEY/" .env
        sed -i "s/LITELLM_SALT_KEY=.*/LITELLM_SALT_KEY=$SALT_KEY/" .env
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
        
        # Add OPENAI_API_KEY if provided
        if [ ! -z "$OPENAI_API_KEY" ]; then
            sed -i "s|# OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
        fi
    fi
    
    echo "✅ Generated secure keys"
    echo ""
    echo "📋 Your Master Key (save this!):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "LITELLM_MASTER_KEY=$MASTER_KEY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "🐳 Starting services with Docker Compose..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🏥 Checking health..."
for i in {1..6}; do
    if curl -s -f http://localhost:4000/health > /dev/null 2>&1; then
        echo "✅ Proxy is healthy!"
        break
    else
        if [ $i -eq 6 ]; then
            echo "⚠️  Proxy is still starting up..."
            echo "   Check logs with: docker compose logs -f litellm"
        else
            echo "   Waiting... ($i/6)"
            sleep 5
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Proxy URL:  http://localhost:4000"
echo "🎨 Admin UI:   http://localhost:4000/ui"
echo "📊 Metrics:    http://localhost:4000/metrics"
echo "🏥 Health:     http://localhost:4000/health"
echo ""
echo "🤖 Available Models (2026):"
echo "   - gpt-5.2      (flagship - best for coding & agents)"
echo "   - gpt-5-mini   (fast & cost-efficient)"
echo "   - gpt-5-nano   (fastest & cheapest)"
echo "   - gpt-4.1      (non-reasoning alternative)"
echo ""
echo "📋 Quick Test:"
echo "   curl -X POST http://localhost:4000/chat/completions \\"
echo "     -H 'Authorization: Bearer YOUR_KEY' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"model\":\"gpt-5-nano\",\"messages\":[{\"role\":\"user\",\"content\":\"Hi!\"}]}'"
echo ""
echo "📚 View logs: docker compose logs -f"
echo "🛑 Stop:      docker compose down"
