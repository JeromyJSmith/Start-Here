#!/bin/bash

# Claude Code Monorepo Test Runner
# Comprehensive testing script following T-1 to T-5 principles

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICES_DIR="${ROOT_DIR}/services"

# Default settings
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_E2E=false
RUN_COVERAGE=true
VERBOSE=false
PARALLEL=true
SERVICES=""
FAIL_FAST=false

# Usage function
usage() {
    cat << EOF
Claude Code Monorepo Test Runner

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -u, --unit-only     Run only unit tests
    -i, --integration   Run only integration tests  
    -e, --e2e           Run end-to-end tests
    -c, --coverage      Generate coverage reports (default: true)
    --no-coverage       Skip coverage generation
    -v, --verbose       Verbose output
    -s, --services      Comma-separated list of services to test
    -p, --parallel      Run tests in parallel (default: true)
    --sequential        Run tests sequentially
    -f, --fail-fast     Stop on first failure
    --clean             Clean test artifacts before running

EXAMPLES:
    $0                                  # Run all unit and integration tests
    $0 --e2e                           # Run all tests including E2E
    $0 -s "frontend,backend"           # Test only frontend and backend
    $0 --unit-only --no-coverage       # Quick unit test run
    $0 --verbose --fail-fast           # Verbose output, stop on first failure

SERVICES:
    Python: superclaude-framework, memory-service, unified-query-service, cognee, memos
    Node.js: cli-tool, claudecodeui-backend, agent-io, memento-mcp
    Frontend: claudecodeui-frontend
    E2E: e2e-tests
EOF
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -u|--unit-only)
                RUN_UNIT=true
                RUN_INTEGRATION=false
                RUN_E2E=false
                ;;
            -i|--integration)
                RUN_UNIT=false
                RUN_INTEGRATION=true
                RUN_E2E=false
                ;;
            -e|--e2e)
                RUN_E2E=true
                ;;
            -c|--coverage)
                RUN_COVERAGE=true
                ;;
            --no-coverage)
                RUN_COVERAGE=false
                ;;
            -v|--verbose)
                VERBOSE=true
                ;;
            -s|--services)
                SERVICES="$2"
                shift
                ;;
            -p|--parallel)
                PARALLEL=true
                ;;
            --sequential)
                PARALLEL=false
                ;;
            -f|--fail-fast)
                FAIL_FAST=true
                ;;
            --clean)
                CLEAN=true
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
        shift
    done
}

# Clean test artifacts
clean_artifacts() {
    log_section "Cleaning Test Artifacts"
    
    find "${ROOT_DIR}" -name "coverage" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${ROOT_DIR}" -name "test-results" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${ROOT_DIR}" -name "playwright-report" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${ROOT_DIR}" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${ROOT_DIR}" -name "*.pyc" -delete 2>/dev/null || true
    find "${ROOT_DIR}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Test artifacts cleaned"
}

# Check if service exists
service_exists() {
    local service=$1
    [[ -d "${SERVICES_DIR}/${service}" ]]
}

# Get service type
get_service_type() {
    local service=$1
    
    if [[ -f "${SERVICES_DIR}/${service}/pyproject.toml" ]] || [[ -f "${SERVICES_DIR}/${service}/requirements.txt" ]]; then
        echo "python"
    elif [[ -f "${SERVICES_DIR}/${service}/package.json" ]]; then
        if [[ "${service}" == "claudecodeui-frontend" ]]; then
            echo "frontend"
        else
            echo "node"
        fi
    else
        echo "unknown"
    fi
}

# Run Python service tests
test_python_service() {
    local service=$1
    local service_dir="${SERVICES_DIR}/${service}"
    
    log_section "Testing Python Service: ${service}"
    
    cd "${service_dir}"
    
    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt || log_warning "Failed to install requirements"
    fi
    
    if [[ -f "pyproject.toml" ]]; then
        pip install -e . || log_warning "Failed to install package"
    fi
    
    # Install test dependencies
    pip install pytest pytest-cov pytest-asyncio pytest-mock || {
        log_error "Failed to install test dependencies for ${service}"
        return 1
    }
    
    # Run tests
    local pytest_args=""
    
    if [[ "${RUN_COVERAGE}" == "true" ]]; then
        pytest_args="${pytest_args} --cov --cov-report=html --cov-report=xml"
    fi
    
    if [[ "${VERBOSE}" == "true" ]]; then
        pytest_args="${pytest_args} -v"
    fi
    
    if [[ "${FAIL_FAST}" == "true" ]]; then
        pytest_args="${pytest_args} -x"
    fi
    
    # Run unit tests
    if [[ "${RUN_UNIT}" == "true" ]]; then
        log_info "Running unit tests for ${service}"
        python -m pytest tests/ ${pytest_args} -m "not integration" || {
            log_error "Unit tests failed for ${service}"
            return 1
        }
    fi
    
    # Run integration tests
    if [[ "${RUN_INTEGRATION}" == "true" ]]; then
        log_info "Running integration tests for ${service}"
        python -m pytest tests/ ${pytest_args} -m "integration" || {
            log_error "Integration tests failed for ${service}"
            return 1
        }
    fi
    
    log_success "Python service ${service} tests completed"
    cd "${ROOT_DIR}"
}

# Run Node.js service tests
test_node_service() {
    local service=$1
    local service_dir="${SERVICES_DIR}/${service}"
    
    log_section "Testing Node.js Service: ${service}"
    
    cd "${service_dir}"
    
    # Install dependencies
    npm ci || {
        log_error "Failed to install dependencies for ${service}"
        return 1
    }
    
    # Run linting if available
    if npm run lint --if-present; then
        log_success "Linting passed for ${service}"
    else
        log_warning "Linting failed or not configured for ${service}"
    fi
    
    # Run tests
    local test_args=""
    
    if [[ "${RUN_COVERAGE}" == "true" ]]; then
        test_args="${test_args} --coverage"
    fi
    
    if [[ "${RUN_UNIT}" == "true" && "${RUN_INTEGRATION}" == "false" ]]; then
        npm run test:unit || {
            log_error "Unit tests failed for ${service}"
            return 1
        }
    elif [[ "${RUN_INTEGRATION}" == "true" && "${RUN_UNIT}" == "false" ]]; then
        npm run test:integration || {
            log_error "Integration tests failed for ${service}"
            return 1
        }
    else
        npm test || {
            log_error "Tests failed for ${service}"
            return 1
        }
    fi
    
    log_success "Node.js service ${service} tests completed"
    cd "${ROOT_DIR}"
}

# Run frontend tests
test_frontend_service() {
    local service=$1
    local service_dir="${SERVICES_DIR}/${service}"
    
    log_section "Testing Frontend Service: ${service}"
    
    cd "${service_dir}"
    
    # Install dependencies
    npm ci || {
        log_error "Failed to install dependencies for ${service}"
        return 1
    }
    
    # Run linting if available
    if npm run lint --if-present; then
        log_success "Linting passed for ${service}"
    fi
    
    # Run tests
    if [[ "${RUN_COVERAGE}" == "true" ]]; then
        npm run test:coverage || {
            log_error "Frontend tests failed for ${service}"
            return 1
        }
    else
        npm run test:run || {
            log_error "Frontend tests failed for ${service}"
            return 1
        }
    fi
    
    # Build to ensure no build errors
    npm run build || {
        log_error "Build failed for ${service}"
        return 1
    }
    
    log_success "Frontend service ${service} tests completed"
    cd "${ROOT_DIR}"
}

# Run E2E tests
test_e2e() {
    log_section "Running E2E Tests"
    
    local e2e_dir="${SERVICES_DIR}/e2e-tests"
    
    if [[ ! -d "${e2e_dir}" ]]; then
        log_warning "E2E tests directory not found, skipping"
        return 0
    fi
    
    cd "${e2e_dir}"
    
    # Install dependencies
    npm ci || {
        log_error "Failed to install E2E test dependencies"
        return 1
    }
    
    # Install Playwright browsers
    npx playwright install --with-deps || {
        log_error "Failed to install Playwright browsers"
        return 1
    }
    
    # Run E2E tests
    npm test || {
        log_error "E2E tests failed"
        return 1
    }
    
    log_success "E2E tests completed"
    cd "${ROOT_DIR}"
}

# Run tests for a single service
test_service() {
    local service=$1
    local service_type
    
    if ! service_exists "${service}"; then
        log_error "Service ${service} does not exist"
        return 1
    fi
    
    service_type=$(get_service_type "${service}")
    
    case "${service_type}" in
        python)
            test_python_service "${service}"
            ;;
        node)
            test_node_service "${service}"
            ;;
        frontend)
            test_frontend_service "${service}"
            ;;
        *)
            log_error "Unknown service type for ${service}"
            return 1
            ;;
    esac
}

# Run all tests
run_tests() {
    local services_to_test=()
    local failed_services=()
    
    # Determine which services to test
    if [[ -n "${SERVICES}" ]]; then
        IFS=',' read -ra services_to_test <<< "${SERVICES}"
    else
        # Test all services
        services_to_test=(
            "superclaude-framework"
            "memory-service"  
            "unified-query-service"
            "cognee"
            "memos"
            "cli-tool"
            "claudecodeui-backend"
            "agent-io"
            "memento-mcp"
            "claudecodeui-frontend"
        )
    fi
    
    log_section "Starting Test Execution"
    log_info "Services to test: ${services_to_test[*]}"
    log_info "Unit tests: ${RUN_UNIT}"
    log_info "Integration tests: ${RUN_INTEGRATION}"
    log_info "E2E tests: ${RUN_E2E}"
    log_info "Coverage: ${RUN_COVERAGE}"
    log_info "Parallel: ${PARALLEL}"
    
    # Test services
    if [[ "${PARALLEL}" == "true" ]]; then
        log_info "Running tests in parallel"
        for service in "${services_to_test[@]}"; do
            (
                test_service "${service}" || {
                    echo "${service}" >> /tmp/failed_services
                }
            ) &
        done
        wait
        
        # Check for failures
        if [[ -f /tmp/failed_services ]]; then
            mapfile -t failed_services < /tmp/failed_services
            rm -f /tmp/failed_services
        fi
    else
        log_info "Running tests sequentially"
        for service in "${services_to_test[@]}"; do
            if ! test_service "${service}"; then
                failed_services+=("${service}")
                if [[ "${FAIL_FAST}" == "true" ]]; then
                    break
                fi
            fi
        done
    fi
    
    # Run E2E tests if requested
    if [[ "${RUN_E2E}" == "true" ]]; then
        if ! test_e2e; then
            failed_services+=("e2e-tests")
        fi
    fi
    
    # Report results
    log_section "Test Results Summary"
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All tests passed! ✅"
        return 0
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    log_info "Claude Code Monorepo Test Runner"
    log_info "Root directory: ${ROOT_DIR}"
    
    # Clean artifacts if requested
    if [[ "${CLEAN}" == "true" ]]; then
        clean_artifacts
    fi
    
    # Check dependencies
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    # Run tests
    if run_tests; then
        log_success "Test runner completed successfully"
        exit 0
    else
        log_error "Test runner completed with failures"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"