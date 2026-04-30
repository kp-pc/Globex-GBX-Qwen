#!/bin/bash
# Globex (GBX) Blockchain - Build and Development Scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help message
show_help() {
    cat << EOF
Globex (GBX) Blockchain - Makefile Alternative

Usage: ./build.sh [command]

Commands:
    install     Install Python dependencies
    test        Run test suite
    lint        Run code linting (if available)
    build       Build Docker image
    up          Start all services with docker-compose
    down        Stop all services
    logs        View live logs
    clean       Clean temporary files and test artifacts
    benchmark   Run performance benchmarks
    help        Show this help message

Examples:
    ./build.sh install
    ./build.sh test
    ./build.sh up
EOF
}

# Install dependencies
do_install() {
    echo_info "Installing Python dependencies..."
    pip install -r requirements.txt
    echo_info "Dependencies installed successfully!"
}

# Run tests
do_test() {
    echo_info "Running test suite..."
    pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html:coverage
    echo_info "Tests completed! Check coverage/ directory for reports."
}

# Run linter
do_lint() {
    echo_info "Running code linting..."
    if command -v flake8 &> /dev/null; then
        flake8 *.py tests/ --max-line-length=120 --ignore=E501,W503
    else
        echo_warn "flake8 not installed. Install with: pip install flake8"
    fi
}

# Build Docker image
do_build() {
    echo_info "Building Docker image..."
    docker build -t globex-gbx .
    echo_info "Docker image built successfully!"
}

# Start services
do_up() {
    echo_info "Starting Globex services..."
    docker-compose up -d
    echo_info "Services started! Dashboard available at http://localhost:8080"
}

# Stop services
do_down() {
    echo_info "Stopping Globex services..."
    docker-compose down
    echo_info "Services stopped."
}

# View logs
do_logs() {
    echo_info "Viewing live logs..."
    docker-compose logs -f
}

# Clean temporary files
do_clean() {
    echo_info "Cleaning temporary files..."
    rm -rf __pycache__/
    rm -rf tests/__pycache__/
    rm -rf .pytest_cache/
    rm -rf coverage/
    rm -rf .coverage
    rm -f test_*.json
    rm -f *.pyc
    echo_info "Cleanup completed!"
}

# Run benchmarks
do_benchmark() {
    echo_info "Running performance benchmarks..."
    python stress_test_dashboard.py --benchmark-only
    echo_info "Benchmarks completed!"
}

# Main command handler
case "${1:-help}" in
    install)
        do_install
        ;;
    test)
        do_test
        ;;
    lint)
        do_lint
        ;;
    build)
        do_build
        ;;
    up)
        do_up
        ;;
    down)
        do_down
        ;;
    logs)
        do_logs
        ;;
    clean)
        do_clean
        ;;
    benchmark)
        do_benchmark
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
