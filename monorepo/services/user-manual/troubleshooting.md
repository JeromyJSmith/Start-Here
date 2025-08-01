# Troubleshooting Guide

Common issues and solutions for the Claude Code Monorepo system. This guide covers everything from initial setup problems to advanced performance tuning.

## 📋 Quick Reference

| Issue Category | Common Symptoms | Quick Fix |
|----------------|-----------------|-----------|
| **Setup Issues** | Services won't start, port conflicts | `make clean && make setup && make dev` |
| **Database Problems** | Connection errors, migration failures | `make db-reset && make restart` |
| **Memory Issues** | High CPU/RAM usage, slow responses | Check container limits, restart services |
| **Network Issues** | Service communication failures | Verify port availability, check firewall |
| **Authentication** | Login failures, token issues | Check API keys, regenerate tokens |

---

## 🚀 Initial Setup Issues

### Services Won't Start

**Symptoms:**
- Docker containers fail to start
- Port binding errors
- Service health checks failing

**Solutions:**

```bash
# 1. Nuclear option - complete reset
make clean
docker system prune -f
make setup
make dev

# 2. Check port availability
netstat -tulpn | grep -E ':(3000|3001|5173|8001|8003|8500|8505|11434)'

# 3. Stop conflicting processes
sudo lsof -i :3000  # Check what's using port 3000
sudo kill -9 <PID>  # Kill conflicting process

# 4. Verify Docker resources
docker system df  # Check disk space
docker stats      # Check resource usage
```

**Check Configuration:**
```bash
# Verify .env file exists and is properly configured
cat .env

# Check Docker Compose configuration
docker-compose config

# Verify all required directories exist
ls -la volumes/
```

### Permission Issues

**Symptoms:**
- Volume mount failures
- File permission errors
- Cannot write to directories

**Solutions:**

```bash
# Fix volume permissions
sudo chown -R $USER:$USER volumes/
sudo chmod -R 755 volumes/

# Fix Docker socket permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Reset volume permissions
make stop
sudo rm -rf volumes/
make setup
make dev
```

### Environment Configuration

**Symptoms:**
- Missing environment variables
- Service configuration errors
- API key authentication failures

**Solutions:**

```bash
# 1. Copy and configure environment file
cp .env.example .env
nano .env  # Edit configuration

# 2. Verify critical environment variables
echo "Required variables:"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-(not set)}"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-(not set)}"
echo "JWT_SECRET: ${JWT_SECRET:-(not set)}"

# 3. Restart services after environment changes
make restart
```

**Required Environment Variables:**
```env
# Core API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
LLAMA_INDEX_API_KEY=your_llamaindex_key_here

# Database Configuration
POSTGRES_DB=claude_code
POSTGRES_USER=claude
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Authentication
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here

# Service URLs
VITE_API_URL=http://localhost:3000
CLAUDE_API_URL=http://localhost:8001
MEMORY_API_URL=http://localhost:8500
UQS_API_URL=http://localhost:8505

# Redis Configuration
REDIS_URL=redis://redis:6379

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password_here
```

---

## 🐳 Docker & Container Issues

### Container Health Check Failures

**Symptoms:**
- Services show as unhealthy
- Intermittent connection issues
- Services restart frequently

**Diagnosis:**

```bash
# Check container health
docker-compose ps

# View container logs
make logs-SERVICE_NAME

# Check resource usage
docker stats

# Inspect container configuration
docker inspect monorepo_SERVICE_NAME_1
```

**Solutions:**

```bash
# 1. Increase health check timeouts
# Edit docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s

# 2. Adjust container resources
services:
  service_name:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'

# 3. Fix dependency order
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

### Image Build Failures

**Symptoms:**
- Docker build errors
- Missing dependencies
- Layer caching issues

**Solutions:**

```bash
# 1. Clear build cache
docker builder prune -f

# 2. Rebuild without cache
docker-compose build --no-cache

# 3. Check Dockerfile syntax
docker-compose config

# 4. Build specific service
make build-SERVICE_NAME

# 5. Check build logs
docker-compose logs --no-color > build.log
```

### Volume Mount Issues

**Symptoms:**
- Data not persisting
- Permission denied errors
- Volume mount failures

**Solutions:**

```bash
# 1. Check volume mounts
docker volume ls
docker volume inspect monorepo_postgres_data

# 2. Fix volume permissions
docker-compose down
sudo chown -R $USER:$USER volumes/
docker-compose up -d

# 3. Recreate volumes
docker-compose down -v
make setup
make dev
```

---

## 🗄️ Database Issues

### PostgreSQL Connection Issues

**Symptoms:**
- Database connection refused
- Authentication failures
- Connection timeouts

**Diagnosis:**

```bash
# Check PostgreSQL status
make shell-postgres
# Inside container:
pg_isready -U claude -d claude_code

# Test connection from other services
docker-compose exec backend psql -h postgres -U claude -d claude_code -c "SELECT 1;"

# Check connection configuration
docker-compose exec backend env | grep POSTGRES
```

**Solutions:**

```bash
# 1. Reset database
make db-reset

# 2. Check database configuration
make shell-postgres
# Inside PostgreSQL:
\l  # List databases
\du # List users
\q  # Exit

# 3. Recreate database with proper permissions
docker-compose exec postgres createdb -U claude claude_code
docker-compose exec postgres psql -U claude -d claude_code -c "GRANT ALL PRIVILEGES ON DATABASE claude_code TO claude;"
```

### Migration Failures

**Symptoms:**
- Migration errors on startup
- Schema inconsistencies
- Data corruption

**Solutions:**

```bash
# 1. Check migration status
make shell-backend
npm run migrate:status

# 2. Reset and rerun migrations
make db-reset
make shell-backend
npm run migrate:up

# 3. Manual migration fix
make shell-postgres
# Run SQL commands manually to fix schema

# 4. Backup before migration attempts
make backup
```

### Redis Connection Issues

**Symptoms:**
- Cache not working
- Session storage failures
- Redis connection errors

**Solutions:**

```bash
# 1. Test Redis connection
make shell-redis
ping
info server
exit

# 2. Clear Redis cache
make shell-redis
flushall

# 3. Check Redis configuration
docker-compose exec redis redis-cli config get "*"
```

---

## 🧠 Memory System Issues

### Cognee Connection Problems

**Symptoms:**
- Cognee service unavailable
- Graph database errors
- Memory storage failures

**Diagnosis:**

```bash
# Check Cognee service health
curl http://localhost:8500/health

# Check Neo4j connection
make shell-neo4j
# Inside Neo4j:
MATCH (n) RETURN count(n);

# Check Cognee logs
make logs-memory-service
```

**Solutions:**

```bash
# 1. Restart memory services
docker-compose restart memory-service neo4j

# 2. Reset Neo4j database
docker-compose stop neo4j
docker volume rm monorepo_neo4j_data
docker-compose up -d neo4j

# 3. Verify Cognee configuration
make shell-memory-service
python3 -c "import cognee; print('Cognee available')"
```

### Memento MCP Issues

**Symptoms:**
- MCP server connection failures
- Key-value storage errors
- Temporal data issues

**Solutions:**

```bash
# 1. Check MCP server status
curl http://localhost:3000/api/mcp/servers/memento/health

# 2. Restart Memento MCP
docker-compose restart memento-mcp

# 3. Clear MCP server cache
rm -rf volumes/mcp-cache/
make restart
```

### Unified Query Service Problems

**Symptoms:**
- Query orchestration failures
- Memory system timeouts
- Result aggregation errors

**Diagnosis:**

```bash
# Check UQS health
curl http://localhost:8505/health

# Test individual memory systems
curl http://localhost:8505/api/systems/health

# Check UQS logs
make logs-unified-query-service
```

**Solutions:**

```bash
# 1. Restart UQS
docker-compose restart unified-query-service

# 2. Check memory system configurations
make shell-unified-query-service
cat config/systems.yaml

# 3. Test query with debug mode
curl -X POST http://localhost:8505/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "unified", "debug": true}'
```

---

## ⚡ Performance Issues

### High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors
- Container restarts

**Diagnosis:**

```bash
# Check system memory usage
free -h
docker stats

# Check individual service memory
docker-compose exec SERVICE_NAME top
docker-compose exec SERVICE_NAME ps aux

# Monitor memory usage over time
watch docker stats
```

**Solutions:**

```bash
# 1. Increase container memory limits
# Edit docker-compose.yml
services:
  service_name:
    deploy:
      resources:
        limits:
          memory: 4G

# 2. Optimize caching
# Reduce cache TTL and size limits
# Clear unnecessary caches
make shell-redis
flushall

# 3. Clean up old data
make backup  # Backup first
make db-reset
# Restore only essential data
```

### Slow Query Performance

**Symptoms:**
- Long response times
- Query timeouts
- High CPU usage

**Solutions:**

```bash
# 1. Analyze query performance
curl http://localhost:8505/api/analytics/performance

# 2. Enable query caching
# Edit unified query service config
cache:
  enabled: true
  ttl: 3600  # 1 hour
  max_size: 1000

# 3. Optimize database queries
make shell-postgres
# Analyze slow queries
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Add database indexes
CREATE INDEX idx_users_email ON users(email);
```

### High CPU Usage

**Symptoms:**
- System responsiveness issues
- Fan noise/heat
- Process timeouts

**Solutions:**

```bash
# 1. Identify CPU-intensive processes
docker stats
top -p $(docker inspect --format '{{.State.Pid}}' monorepo_SERVICE_1)

# 2. Limit CPU usage
# Edit docker-compose.yml
services:
  service_name:
    deploy:
      resources:
        limits:
          cpus: '2.0'

# 3. Optimize AI model usage
# Use smaller models
# Implement request queuing
# Add rate limiting
```

---

## 🔌 Network & API Issues

### Service Communication Failures

**Symptoms:**
- Internal API calls failing
- Service discovery issues
- Network timeouts

**Diagnosis:**

```bash
# Test service connectivity
docker-compose exec frontend ping backend
docker-compose exec backend ping postgres

# Check port bindings
docker-compose ps
netstat -tulpn

# Test API endpoints
curl http://localhost:3000/health
curl http://localhost:8001/health
curl http://localhost:8500/health
```

**Solutions:**

```bash
# 1. Check network configuration
docker network ls
docker network inspect monorepo_default

# 2. Restart networking
docker-compose down
docker network prune
docker-compose up -d

# 3. Update service references
# Use service names instead of localhost in internal communication
# Example: http://backend:3000 instead of http://localhost:3000
```

### API Rate Limiting Issues

**Symptoms:**
- 429 Too Many Requests errors
- API quota exceeded
- Service unavailable errors

**Solutions:**

```bash
# 1. Check API usage
curl http://localhost:3001/api/analytics/usage

# 2. Implement request caching
# Add Redis-based response caching
# Cache frequent queries

# 3. Add rate limiting configuration
# Edit API service configuration
rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 10
```

### External API Issues

**Symptoms:**
- Third-party API failures
- Authentication errors
- Quota exceeded

**Solutions:**

```bash
# 1. Verify API keys
echo "Anthropic API Key: ${ANTHROPIC_API_KEY:0:10}..."
echo "LlamaIndex API Key: ${LLAMA_INDEX_API_KEY:0:10}..."

# 2. Test API connectivity
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models

# 3. Implement fallback strategies
# Use local Ollama models when external APIs fail
# Add circuit breaker patterns
# Implement retry logic with exponential backoff
```

---

## 🔐 Authentication & Security Issues

### JWT Token Issues

**Symptoms:**
- Authentication failures
- Token expiration errors
- Invalid signature errors

**Solutions:**

```bash
# 1. Regenerate JWT secret
openssl rand -hex 32
# Update JWT_SECRET in .env file

# 2. Clear existing tokens
make shell-redis
flushall

# 3. Test token generation
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

### API Key Problems

**Symptoms:**
- API authentication failures
- Unauthorized errors
- Service access denied

**Solutions:**

```bash
# 1. Verify API key format
echo $ANTHROPIC_API_KEY | wc -c  # Should be proper length
echo $ANTHROPIC_API_KEY | grep -E '^sk-ant-' # Should start with sk-ant-

# 2. Test API key validity
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models

# 3. Regenerate API keys
# Visit Anthropic Console: https://console.anthropic.com/
# Generate new API key
# Update .env file
# Restart services
make restart
```

### Session Management Issues

**Symptoms:**
- Session not persisting  
- Login state lost
- Multiple session conflicts

**Solutions:**

```bash
# 1. Check session storage
make shell-redis
keys session:*

# 2. Configure session settings
# Edit backend configuration
session: {
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false, // true in production
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}

# 3. Clear session data
make shell-redis
del session:*
```

---

## 📊 Analytics & Monitoring Issues

### Analytics Dashboard Not Loading

**Symptoms:**
- Dashboard shows no data
- WebSocket connection failures
- Charts not rendering

**Solutions:**

```bash
# 1. Check analytics service
curl http://localhost:3001/health

# 2. Test WebSocket connection
# In browser console:
const ws = new WebSocket('ws://localhost:3001/ws/analytics');
ws.onopen = () => console.log('Connected');
ws.onerror = (e) => console.error('Error:', e);

# 3. Check data collection
curl http://localhost:3001/api/analytics/sessions
curl http://localhost:3001/api/analytics/metrics
```

### Missing Analytics Data

**Symptoms:**
- No session tracking
- Metrics not updating
- Incomplete data

**Solutions:**

```bash
# 1. Verify data collection is enabled
make shell-cli-tool
# Check analytics configuration
cat src/analytics.js

# 2. Test data collection manually
curl -X POST http://localhost:3001/api/analytics/session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "event": "start"}'

# 3. Clear and restart data collection
make shell-redis
flushall
make restart
```

---

## 🔧 Service-Specific Issues

### Claude Code Service Issues

**Symptoms:**
- Commands not executing
- Response timeouts
- Context loss

**Solutions:**

```bash
# 1. Check Claude Code health
curl http://localhost:8001/health

# 2. Test basic functionality
make shell-claude-code
claude --version
claude "echo 'test command'"

# 3. Clear Claude Code cache
rm -rf ~/.claude/cache/
make restart
```

### SuperClaude Framework Issues

**Symptoms:**
- Personas not activating
- Commands not recognized
- MCP server integration failures

**Solutions:**

```bash
# 1. Check SuperClaude status
curl http://localhost:8001/api/framework/info

# 2. Test command execution
curl -X POST http://localhost:8001/api/commands/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "sc:help"}'

# 3. Verify MCP server connections
curl http://localhost:8001/api/mcp/servers
```

### Frontend Issues

**Symptoms:**
- UI not loading
- API connection failures
- Component errors

**Solutions:**

```bash
# 1. Check frontend logs
make logs-frontend

# 2. Test API connectivity from frontend
make shell-frontend
curl http://backend:3000/health

# 3. Clear browser cache and rebuild
make build-frontend
# Clear browser cache and hard refresh
```

---

## 🆘 Emergency Recovery Procedures

### Complete System Reset

When everything is broken:

```bash
# 1. Stop all services
make stop

# 2. Remove all containers and volumes
docker-compose down -v --remove-orphans
docker system prune -af
docker volume prune -f

# 3. Reset file permissions
sudo chown -R $USER:$USER .
chmod -R 755 volumes/

# 4. Recreate from scratch
make setup
make install-deps
make dev

# 5. Verify system health
sleep 60  # Wait for startup
make health
```

### Backup and Restore

Create backups before major changes:

```bash
# Create backup
make backup

# Manual backup of critical data
docker run --rm -v monorepo_postgres_data:/data \
  -v $(PWD)/emergency-backup:/backup alpine \
  tar czf /backup/postgres-emergency.tar.gz -C /data .

docker run --rm -v monorepo_redis_data:/data \
  -v $(PWD)/emergency-backup:/backup alpine \
  tar czf /backup/redis-emergency.tar.gz -C /data .

# Restore from backup
docker run --rm -v monorepo_postgres_data:/data \
  -v $(PWD)/emergency-backup:/backup alpine \
  tar xzf /backup/postgres-emergency.tar.gz -C /data
```

### Performance Emergency

When system is critically slow:

```bash
# 1. Immediate resource cleanup
docker system prune -f
make shell-redis && flushall

# 2. Restart resource-intensive services
docker-compose restart unified-query-service
docker-compose restart memory-service
docker-compose restart ollama

# 3. Reduce system load
# Temporarily disable non-essential services
docker-compose stop n8n
docker-compose stop dashboard

# 4. Monitor recovery
watch docker stats
```

---

## 📞 Getting Additional Help

### Diagnostic Information Collection

When seeking help, collect this information:

```bash
# System information
echo "=== System Info ===" > diagnostic.log
uname -a >> diagnostic.log
docker --version >> diagnostic.log
docker-compose --version >> diagnostic.log

# Service status
echo "=== Service Status ===" >> diagnostic.log
docker-compose ps >> diagnostic.log

# Resource usage
echo "=== Resource Usage ===" >> diagnostic.log
docker stats --no-stream >> diagnostic.log

# Recent logs
echo "=== Recent Logs ===" >> diagnostic.log
docker-compose logs --tail=50 >> diagnostic.log

# Configuration
echo "=== Configuration ===" >> diagnostic.log
docker-compose config >> diagnostic.log
```

### Log Analysis

```bash
# Search for specific errors
make logs | grep -i error
make logs | grep -i timeout
make logs | grep -i connection

# Export logs for analysis
make logs > system.log 2>&1

# Analyze error patterns
grep -E "(ERROR|FATAL|CRITICAL)" system.log | sort | uniq -c
```

### Health Check Script

Create a comprehensive health check:

```bash
#!/bin/bash
# health_check.sh

echo "=== Claude Code Monorepo Health Check ==="

# Check required ports
PORTS=(3000 3001 5173 8001 8003 8500 8505 11434)
for port in "${PORTS[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        echo "✅ Port $port is available"
    else
        echo "❌ Port $port is not available"
    fi
done

# Check service health endpoints
ENDPOINTS=(
    "http://localhost:3000/health"
    "http://localhost:3001/api/health" 
    "http://localhost:8001/health"
    "http://localhost:8500/health"
    "http://localhost:8505/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s "$endpoint" > /dev/null; then
        echo "✅ $endpoint is responding"
    else
        echo "❌ $endpoint is not responding"
    fi
done

# Check Docker resources
echo "=== Docker Resources ==="
docker system df

echo "=== Memory Usage ==="
free -h

echo "=== Disk Usage ==="
df -h

echo "Health check complete!"
```

Make it executable and run:
```bash
chmod +x health_check.sh
./health_check.sh
```

This troubleshooting guide covers the most common issues you might encounter with the Claude Code Monorepo system. For issues not covered here, check the service-specific documentation or seek help with the diagnostic information collected above.