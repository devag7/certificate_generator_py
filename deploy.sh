#!/bin/bash

# =============================================================================
# Certificate Generation System Deployment Script
# =============================================================================
# Author: devag7 (Deva Garwalla)
# Description: Production deployment script with monitoring and management
# Usage: ./deploy.sh [start|stop|restart|status|logs]
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/my_project_env"
CELERY_APP="tasks"
WORKER_NAME="certificate_worker"
BEAT_NAME="certificate_beat"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found at $VENV_DIR"
        log_info "Run ./setup.sh first to set up the environment"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    source "$VENV_DIR/bin/activate"
}

# Check if Redis is running
check_redis() {
    if ! redis-cli ping > /dev/null 2>&1; then
        log_warning "Redis is not running. Starting Redis..."
        if command -v brew > /dev/null 2>&1; then
            brew services start redis
            sleep 2
        else
            log_error "Please start Redis manually"
            exit 1
        fi
    fi
}

# Start Celery worker
start_worker() {
    log_info "Starting Celery worker..."
    check_venv
    activate_venv
    check_redis
    
    cd "$PROJECT_DIR"
    
    celery -A $CELERY_APP worker \
        --loglevel=info \
        --hostname=$WORKER_NAME@%h \
        --pidfile="$PID_DIR/worker.pid" \
        --logfile="$LOG_DIR/worker.log" \
        --detach \
        --concurrency=4
    
    log_success "Celery worker started"
}

# Start Celery beat (scheduler)
start_beat() {
    log_info "Starting Celery beat scheduler..."
    check_venv
    activate_venv
    check_redis
    
    cd "$PROJECT_DIR"
    
    celery -A $CELERY_APP beat \
        --loglevel=info \
        --pidfile="$PID_DIR/beat.pid" \
        --logfile="$LOG_DIR/beat.log" \
        --detach
    
    log_success "Celery beat started"
}

# Start monitoring (Flower)
start_monitor() {
    log_info "Starting Celery monitoring (Flower)..."
    check_venv
    activate_venv
    check_redis
    
    cd "$PROJECT_DIR"
    
    # Install flower if not present
    pip install flower > /dev/null 2>&1 || true
    
    celery -A $CELERY_APP flower \
        --port=5555 \
        --address=127.0.0.1 \
        --pidfile="$PID_DIR/flower.pid" \
        --logfile="$LOG_DIR/flower.log" \
        --detach
    
    log_success "Flower monitoring started at http://localhost:5555"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    # Stop worker
    if [ -f "$PID_DIR/worker.pid" ]; then
        WORKER_PID=$(cat "$PID_DIR/worker.pid")
        if kill -0 "$WORKER_PID" 2>/dev/null; then
            kill -TERM "$WORKER_PID"
            log_success "Celery worker stopped"
        fi
        rm -f "$PID_DIR/worker.pid"
    fi
    
    # Stop beat
    if [ -f "$PID_DIR/beat.pid" ]; then
        BEAT_PID=$(cat "$PID_DIR/beat.pid")
        if kill -0 "$BEAT_PID" 2>/dev/null; then
            kill -TERM "$BEAT_PID"
            log_success "Celery beat stopped"
        fi
        rm -f "$PID_DIR/beat.pid"
    fi
    
    # Stop flower
    if [ -f "$PID_DIR/flower.pid" ]; then
        FLOWER_PID=$(cat "$PID_DIR/flower.pid")
        if kill -0 "$FLOWER_PID" 2>/dev/null; then
            kill -TERM "$FLOWER_PID"
            log_success "Flower monitoring stopped"
        fi
        rm -f "$PID_DIR/flower.pid"
    fi
}

# Check service status
check_status() {
    echo -e "${BLUE}Certificate Generation System Status${NC}"
    echo "===================================="
    
    # Check Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "Redis: ${GREEN}Running${NC}"
    else
        echo -e "Redis: ${RED}Not Running${NC}"
    fi
    
    # Check Celery worker
    if [ -f "$PID_DIR/worker.pid" ]; then
        WORKER_PID=$(cat "$PID_DIR/worker.pid")
        if kill -0 "$WORKER_PID" 2>/dev/null; then
            echo -e "Celery Worker: ${GREEN}Running${NC} (PID: $WORKER_PID)"
        else
            echo -e "Celery Worker: ${RED}Not Running${NC} (stale PID file)"
            rm -f "$PID_DIR/worker.pid"
        fi
    else
        echo -e "Celery Worker: ${RED}Not Running${NC}"
    fi
    
    # Check Celery beat
    if [ -f "$PID_DIR/beat.pid" ]; then
        BEAT_PID=$(cat "$PID_DIR/beat.pid")
        if kill -0 "$BEAT_PID" 2>/dev/null; then
            echo -e "Celery Beat: ${GREEN}Running${NC} (PID: $BEAT_PID)"
        else
            echo -e "Celery Beat: ${RED}Not Running${NC} (stale PID file)"
            rm -f "$PID_DIR/beat.pid"
        fi
    else
        echo -e "Celery Beat: ${RED}Not Running${NC}"
    fi
    
    # Check Flower
    if [ -f "$PID_DIR/flower.pid" ]; then
        FLOWER_PID=$(cat "$PID_DIR/flower.pid")
        if kill -0 "$FLOWER_PID" 2>/dev/null; then
            echo -e "Flower Monitor: ${GREEN}Running${NC} (PID: $FLOWER_PID) - http://localhost:5555"
        else
            echo -e "Flower Monitor: ${RED}Not Running${NC} (stale PID file)"
            rm -f "$PID_DIR/flower.pid"
        fi
    else
        echo -e "Flower Monitor: ${RED}Not Running${NC}"
    fi
    
    echo
    echo "System Information:"
    echo "=================="
    echo "Project Directory: $PROJECT_DIR"
    echo "Virtual Environment: $VENV_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "PID Directory: $PID_DIR"
}

# Show logs
show_logs() {
    local service=${1:-worker}
    local lines=${2:-50}
    
    case $service in
        worker)
            log_file="$LOG_DIR/worker.log"
            ;;
        beat)
            log_file="$LOG_DIR/beat.log"
            ;;
        flower)
            log_file="$LOG_DIR/flower.log"
            ;;
        *)
            log_error "Unknown service: $service"
            log_info "Available services: worker, beat, flower"
            exit 1
            ;;
    esac
    
    if [ -f "$log_file" ]; then
        log_info "Showing last $lines lines of $service logs:"
        echo "============================================"
        tail -n "$lines" "$log_file"
    else
        log_warning "Log file not found: $log_file"
    fi
}

# Run health check
health_check() {
    log_info "Running system health check..."
    check_venv
    activate_venv
    
    cd "$PROJECT_DIR"
    python3 -c "
import tasks
import json

try:
    health = tasks.health_check()
    print(json.dumps(health, indent=2))
except Exception as e:
    print(f'Health check failed: {e}')
    exit(1)
"
}

# Run test certificate generation
test_generate() {
    log_info "Testing certificate generation..."
    check_venv
    activate_venv
    
    cd "$PROJECT_DIR"
    ASYNC_MODE=false python3 producer.py
}

# Main command handler
case "${1:-help}" in
    start)
        echo -e "${GREEN}🚀 Starting Certificate Generation System${NC}"
        start_worker
        start_beat
        start_monitor
        echo
        check_status
        ;;
    stop)
        echo -e "${RED}🛑 Stopping Certificate Generation System${NC}"
        stop_services
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting Certificate Generation System${NC}"
        stop_services
        sleep 2
        start_worker
        start_beat
        start_monitor
        echo
        check_status
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs "${2:-worker}" "${3:-50}"
        ;;
    health)
        health_check
        ;;
    test)
        test_generate
        ;;
    monitor)
        log_info "Opening monitoring dashboard..."
        open http://localhost:5555 2>/dev/null || log_info "Open http://localhost:5555 in your browser"
        ;;
    help|*)
        echo -e "${BLUE}Certificate Generation System Deployment Manager${NC}"
        echo "Author: devag7 (Deva Garwalla)"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  start     - Start all services (worker, beat, monitor)"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Show service status"
        echo "  logs      - Show logs [service] [lines]"
        echo "            Services: worker, beat, flower"
        echo "  health    - Run health check"
        echo "  test      - Test certificate generation"
        echo "  monitor   - Open monitoring dashboard"
        echo "  help      - Show this help message"
        echo
        echo "Examples:"
        echo "  $0 start                    # Start all services"
        echo "  $0 logs worker 100          # Show last 100 worker log lines"
        echo "  $0 status                   # Check system status"
        ;;
esac
