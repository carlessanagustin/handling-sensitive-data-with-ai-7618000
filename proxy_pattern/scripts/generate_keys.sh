#!/bin/bash
# Generate secure keys for LiteLLM proxy
# This script generates cryptographically secure keys for your .env file

set -e  # Exit on error

echo "🔐 LiteLLM Proxy - Secure Key Generator"
echo "========================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  Warning: .env file already exists!"
    read -p "Do you want to overwrite existing keys? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Existing .env file preserved."
        exit 1
    fi
fi

# Copy template if .env doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ Created .env from template"
    else
        echo "❌ Error: .env.template not found!"
        exit 1
    fi
fi

echo ""
echo "Generating secure keys..."
echo ""

# Generate Master Key
MASTER_KEY="sk-$(openssl rand -hex 32)"
echo "✅ Generated LITELLM_MASTER_KEY"

# Generate Salt Key
SALT_KEY=$(openssl rand -base64 32)
echo "✅ Generated LITELLM_SALT_KEY"

# Generate PostgreSQL Password
POSTGRES_PASSWORD=$(openssl rand -base64 32)
echo "✅ Generated POSTGRES_PASSWORD"

# Generate Redis Password
REDIS_PASSWORD=$(openssl rand -base64 32)
echo "✅ Generated REDIS_PASSWORD"

echo ""
echo "Updating .env file..."
echo ""

# Update .env file (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$MASTER_KEY/" .env
    sed -i '' "s/LITELLM_SALT_KEY=.*/LITELLM_SALT_KEY=$SALT_KEY/" .env
    sed -i '' "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i '' "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
else
    # Linux
    sed -i "s/LITELLM_MASTER_KEY=.*/LITELLM_MASTER_KEY=$MASTER_KEY/" .env
    sed -i "s/LITELLM_SALT_KEY=.*/LITELLM_SALT_KEY=$SALT_KEY/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
fi

echo "✅ All keys generated and saved to .env"
echo ""
echo "📋 Key Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "LITELLM_MASTER_KEY: ${MASTER_KEY:0:20}... ($(echo -n $MASTER_KEY | wc -c | tr -d ' ') characters)"
echo "LITELLM_SALT_KEY:   ${SALT_KEY:0:20}... ($(echo -n $SALT_KEY | wc -c | tr -d ' ') characters)"
echo "POSTGRES_PASSWORD:  ${POSTGRES_PASSWORD:0:20}... ($(echo -n $POSTGRES_PASSWORD | wc -c | tr -d ' ') characters)"
echo "REDIS_PASSWORD:     ${REDIS_PASSWORD:0:20}... ($(echo -n $REDIS_PASSWORD | wc -c | tr -d ' ') characters)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 🔒 Never commit .env to version control!"
echo "2. 🔒 Store these keys in a secure password manager"
echo "3. 🔒 LITELLM_SALT_KEY CANNOT be changed after first use!"
echo "4. 🔒 Backup your .env file in a secure location"
echo "5. 🔒 Rotate LITELLM_MASTER_KEY regularly"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "1. Review and edit .env to add your LLM provider API keys"
echo "2. Configure models in litellm_config.yaml"
echo "3. Run: docker compose up -d"
echo ""
echo "✨ Setup complete! Your proxy is ready to start."
