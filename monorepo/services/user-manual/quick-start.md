# Quick Start Guide

Get the Claude Code Monorepo up and running in 5 minutes!

## 📋 Prerequisites

Before starting, ensure you have:

- **Docker & Docker Compose** - For container orchestration
- **Node.js 18+** - For local development (optional)
- **pnpm 8+** - For Node.js package management (optional)
- **Python 3.11+** - For Python services (optional)
- **Git** - For version control

### Quick Prerequisites Check

```bash
# Check Docker
docker --version && docker-compose --version

# Check Node.js and pnpm (optional)
node --version && pnpm --version

# Check Python (optional)
python3 --version
```

## 🚀 5-Minute Setup

### Step 1: Clone and Setup (1 minute)

```bash
# Clone the repository
git clone <repository-url>
cd monorepo

# Initial setup - creates .env file and directories
make setup
```

This creates:
- `.env` file from template
- Required directories (`volumes/postgres`, `volumes/redis`, etc.)
- SSL certificate directory

### Step 2: Start All Services (3 minutes)

```bash
# Start all services with hot reload
make dev

# OR start in background (recommended for first run)
make dev-detached
```

This will:
- Build all Docker images
- Start 12+ services in containers
- Set up databases and dependencies
- Enable hot reload for development

### Step 3: Verify Everything Works (1 minute)

```bash
# Check service health and get all URLs
make health
```

You should see all services running and these URLs available:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000
- **Analytics Dashboard**: http://localhost:3001
- **Memory Service**: http://localhost:8500
- **n8n Automation**: http://localhost:5678

## 🎯 First Steps After Setup

### 1. Access the Web Interface

Visit http://localhost:5173 to see the Claude Code web interface:
- Modern React frontend
- Authentication system
- File browser and editor
- Chat interface with Claude

### 2. Try the Analytics Dashboard

Visit http://localhost:3001 for real-time monitoring:
- Live session tracking
- Conversation history
- Performance metrics
- System health status

### 3. Test Claude Code Integration

If you have Claude Code installed locally:

```bash
# Navigate to any project
cd your-project

# Test basic Claude Code functionality
claude --help

# Try SuperClaude commands (if installed)
claude /sc:help
```

### 4. Explore Memory Services

The system includes three memory backends:
- **Cognee**: Semantic graph memory
- **Memento MCP**: Key-value memory store
- **MemOS**: Multi-type memory operations

Access the unified query interface at http://localhost:8505.

## 🔧 Common First-Time Tasks

### Install Dependencies (if needed)

```bash
# Install all dependencies
make install-deps

# Or install specific language deps
make install-python  # Python services
make install-node    # Node.js services
```

### View Logs

```bash
# View all service logs
make logs

# View specific service logs
make logs-frontend
make logs-backend
make logs-superclaude
```

### Access Service Shells

```bash
# Access any service for debugging
make shell-frontend
make shell-backend
make shell-superclaude
make shell-postgres
make shell-redis
```

## 🛠️ Development Workflow

### Hot Reload Development

All services support hot reload in development:

```bash
# Start with hot reload (foreground)
make dev

# Make changes to any service code
# Changes are automatically reflected
```

### Service-Specific Development

```bash
# Work on frontend only
docker-compose up claudecodeui-frontend

# Work on backend only  
docker-compose up claudecodeui-backend

# Work on SuperClaude framework
docker-compose up superclaude-framework
```

### Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-python
make test-node
make test-integration
```

## 🌐 Service Overview

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| Frontend | 5173 | React web interface | ✅ Ready |
| Backend API | 3000 | Express.js server | ✅ Ready |
| SuperClaude | 8001 | AI framework | ✅ Ready |
| CLI Analytics | 3001 | Real-time monitoring | ✅ Ready |
| Memory Service | 8500 | Memory integration | ✅ Ready |
| Unified Query | 8505 | Multi-memory queries | 🚧 Beta |
| GenAI Stack | 8003 | AI model stack | ✅ Ready |
| n8n Automation | 5678 | Workflow engine | ✅ Ready |
| Ollama | 11434 | Local LLM server | ✅ Ready |
| Neo4j | 7474 | Graph database | ✅ Ready |
| PostgreSQL | 5432 | Primary database | ✅ Ready |
| Redis | 6379 | Cache & sessions | ✅ Ready |

## 🎮 Try These Examples

### 1. Web Interface Usage

1. Open http://localhost:5173
2. Log in (default credentials in `.env`)
3. Try the file browser
4. Start a chat with Claude
5. Upload a document for processing

### 2. API Testing

```bash
# Test backend API
curl http://localhost:3000/health

# Test memory service
curl http://localhost:8500/health

# Test unified query service  
curl http://localhost:8505/api/query -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "mode": "unified"}'
```

### 3. Memory System Integration

```bash
# Access the memory service shell
make shell-memory

# Test Cognee integration
python3 -c "import cognee; print('Cognee ready')"

# Test Neo4j connection
make shell-neo4j
```

## 🆘 Quick Troubleshooting

### Services Won't Start

```bash
# Clean everything and start fresh
make clean
make setup
make dev
```

### Port Conflicts

Check your `.env` file and ensure these ports are free:
- 3000, 3001, 5173, 5678, 7474, 8001, 8003, 8500, 8505, 11434

### Database Issues

```bash
# Reset databases
make db-reset

# Check database status
make shell-postgres
make shell-redis
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER volumes/
```

## 📚 Next Steps

Now that you have everything running:

1. **Learn the Commands**: Check [Command Reference](./commands/README.md)
2. **Explore Services**: Read individual service guides in [Services](./services/)
3. **Try Examples**: Look at [Example Projects](./examples/README.md)
4. **Configure**: Review [Configuration Guide](./configuration.md)
5. **Develop**: Follow [Development Workflows](./workflows.md)

## 🏁 You're Ready!

Congratulations! You now have a fully functional Claude Code Monorepo system running locally. The system includes:

- ✅ AI-powered coding assistant
- ✅ Multiple memory systems
- ✅ Web interface and API
- ✅ Real-time analytics
- ✅ Workflow automation
- ✅ Development tools

**What's Next?** 
- Try creating your first project with Claude Code
- Explore the analytics dashboard
- Test the memory integration features
- Set up your development workflow

Need help? Check the [Troubleshooting Guide](./troubleshooting.md) or browse the rest of this manual for detailed information on each component.