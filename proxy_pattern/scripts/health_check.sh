#!/bin/bash
# Health check script for LiteLLM proxy
# Checks the status of all services and reports health

set -e

echo "🏥 LiteLLM Proxy - Health Check"
echo "================================"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service=$1
    local container=$2
    
    if docker compose ps | grep -q "${container}.*Up"; then
        echo -e "${GREEN}✅ $service is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service is not running${NC}"
        return 1
    fi
}

# Function to check endpoint
check_endpoint() {
    local name=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not responding${NC}"
        return 1
    fi
}

# Check Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

echo "📦 Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check each service
ALL_HEALTHY=true

check_service "PostgreSQL" "litellm_postgres" || ALL_HEALTHY=false
check_service "Redis" "litellm_redis" || ALL_HEALTHY=false
check_service "LiteLLM Proxy" "litellm_proxy" || ALL_HEALTHY=false

echo ""
echo "🌐 Endpoint Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check endpoints
PROXY_URL="http://localhost:${LITELLM_PORT:-4000}"

check_endpoint "Health endpoint" "${PROXY_URL}/health" || ALL_HEALTHY=false
check_endpoint "Metrics endpoint" "${PROXY_URL}/metrics" || ALL_HEALTHY=false

echo ""
echo "💾 Resource Usage:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get container stats
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    litellm_postgres litellm_redis litellm_proxy 2>/dev/null || echo "Unable to fetch stats"

echo ""
echo "🗄️  Database Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check database connection
if docker compose exec -T postgres psql -U "${POSTGRES_USER:-litellm_user}" -d "${POSTGRES_DB:-litellm}" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
    
    # Get database size
    DB_SIZE=$(docker compose exec -T postgres psql -U "${POSTGRES_USER:-litellm_user}" -d "${POSTGRES_DB:-litellm}" -t -c "SELECT pg_size_pretty(pg_database_size('${POSTGRES_DB:-litellm}'));" 2>/dev/null | xargs)
    echo "Database size: $DB_SIZE"
    
    # Get table count
    TABLE_COUNT=$(docker compose exec -T postgres psql -U "${POSTGRES_USER:-litellm_user}" -d "${POSTGRES_DB:-litellm}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
    echo "Tables: $TABLE_COUNT"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    ALL_HEALTHY=false
fi

echo ""
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All systems operational${NC}"
    echo ""
    echo "Proxy URL: ${PROXY_URL}"
    echo "Admin UI: ${PROXY_URL}/ui"
    exit 0
else
    echo -e "${RED}❌ Some systems are not healthy${NC}"
    echo ""
    echo "Run 'docker compose logs' to see detailed logs"
    echo "Run 'docker compose up -d' to start stopped services"
    exit 1
fi
