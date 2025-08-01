#!/bin/bash
# Health check script for Claude Code Monorepo

set -e

echo "🏥 Claude Code Monorepo Health Check"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local service=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $service..."
    
    if curl -f -s -o /dev/null "$url"; then
        echo -e " ${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e " ${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Function to check Docker service
check_docker_service() {
    local service=$1
    
    echo -n "Checking Docker service $service..."
    
    if docker-compose ps -q $service | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy\|starting"; then
        echo -e " ${GREEN}✅ Running${NC}"
        return 0
    elif docker-compose ps -q $service >/dev/null 2>&1; then
        echo -e " ${YELLOW}⚠️  No health check${NC}"
        return 0
    else
        echo -e " ${RED}❌ Not running${NC}"
        return 1
    fi
}

echo ""
echo "🐳 Docker Services:"
echo "==================="

DOCKER_HEALTHY=0

check_docker_service "superclaude-framework" || DOCKER_HEALTHY=1
check_docker_service "claude-code" || DOCKER_HEALTHY=1
check_docker_service "genai-stack" || DOCKER_HEALTHY=1
check_docker_service "cli-tool" || DOCKER_HEALTHY=1
check_docker_service "claudecodeui-frontend" || DOCKER_HEALTHY=1
check_docker_service "claudecodeui-backend" || DOCKER_HEALTHY=1
check_docker_service "claudecodeui-plugin" || DOCKER_HEALTHY=1
check_docker_service "n8n-nodes-siteboon" || DOCKER_HEALTHY=1
check_docker_service "postgres" || DOCKER_HEALTHY=1
check_docker_service "redis" || DOCKER_HEALTHY=1
check_docker_service "ollama" || DOCKER_HEALTHY=1

echo ""
echo "🌐 HTTP Endpoints:"
echo "=================="

HTTP_HEALTHY=0

check_service "Frontend" "http://localhost:5173" || HTTP_HEALTHY=1
check_service "Backend API" "http://localhost:3000/api/health" || HTTP_HEALTHY=1
check_service "SuperClaude" "http://localhost:8001" || HTTP_HEALTHY=1
check_service "GenAI Stack" "http://localhost:8003" || HTTP_HEALTHY=1
check_service "CLI Analytics" "http://localhost:3001" || HTTP_HEALTHY=1
check_service "n8n" "http://localhost:5678" || HTTP_HEALTHY=1
check_service "Ollama" "http://localhost:11434" || HTTP_HEALTHY=1

echo ""
echo "💾 Database Connections:"
echo "========================"

DB_HEALTHY=0

echo -n "Checking PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U claude >/dev/null 2>&1; then
    echo -e " ${GREEN}✅ Connected${NC}"
else
    echo -e " ${RED}❌ Not connected${NC}"
    DB_HEALTHY=1
fi

echo -n "Checking Redis..."
if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo -e " ${GREEN}✅ Connected${NC}"
else
    echo -e " ${RED}❌ Not connected${NC}"
    DB_HEALTHY=1
fi

echo ""
echo "📊 System Resources:"
echo "==================="

# Docker system info
echo "Docker system info:"
docker system df

echo ""
echo "Container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "📋 Summary:"
echo "==========="

OVERALL_HEALTH=0

if [ $DOCKER_HEALTHY -eq 0 ]; then
    echo -e "Docker Services: ${GREEN}✅ All healthy${NC}"
else
    echo -e "Docker Services: ${RED}❌ Some issues${NC}"
    OVERALL_HEALTH=1
fi

if [ $HTTP_HEALTHY -eq 0 ]; then
    echo -e "HTTP Endpoints: ${GREEN}✅ All responding${NC}"
else
    echo -e "HTTP Endpoints: ${RED}❌ Some unreachable${NC}"
    OVERALL_HEALTH=1
fi

if [ $DB_HEALTHY -eq 0 ]; then
    echo -e "Databases: ${GREEN}✅ All connected${NC}"
else
    echo -e "Databases: ${RED}❌ Connection issues${NC}"
    OVERALL_HEALTH=1
fi

echo ""
if [ $OVERALL_HEALTH -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems healthy!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some systems need attention${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  make logs          - View all logs"
    echo "  make restart       - Restart all services"
    echo "  make clean && make dev - Clean restart"
    exit 1
fi