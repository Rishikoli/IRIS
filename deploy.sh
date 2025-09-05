#!/bin/bash
# IRIS RegTech Platform - Demo Deployment Script
# Automated setup for complete demo environment

set -e  # Exit on any error

echo "🚀 IRIS RegTech Platform - Demo Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/data
    mkdir -p backend/uploads
    mkdir -p logs
    
    print_success "Directories created"
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cat > .env << EOF
# IRIS RegTech Platform Environment Configuration
ENVIRONMENT=production
GEMINI_API_KEY=demo_key_replace_with_actual
FMP_API_KEY=demo_key_replace_with_actual
DATABASE_URL=sqlite:///./data/iris_regtech.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
CORS_ALLOW_ALL=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
EOF
        print_warning "Created .env file with demo keys. Please update with actual API keys for full functionality."
    else
        print_success "Environment file already exists"
    fi
}

# Build and start services
deploy_services() {
    print_status "Building and starting IRIS services..."
    
    # Stop any existing containers
    docker-compose down --remove-orphans
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for backend
    print_status "Waiting for backend service..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Backend service is healthy"
            break
        fi
        
        counter=$((counter + 1))
        sleep 1
        
        if [ $counter -eq $timeout ]; then
            print_error "Backend service failed to start within $timeout seconds"
            docker-compose logs backend
            exit 1
        fi
    done
    
    # Wait for frontend
    print_status "Waiting for frontend service..."
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost/health &> /dev/null; then
            print_success "Frontend service is healthy"
            break
        fi
        
        counter=$((counter + 1))
        sleep 1
        
        if [ $counter -eq $timeout ]; then
            print_error "Frontend service failed to start within $timeout seconds"
            docker-compose logs frontend
            exit 1
        fi
    done
}

# Initialize database and sample data
initialize_database() {
    print_status "Initializing database with sample data..."
    
    # Create database indexes for performance
    docker-compose exec backend python app/database_indexes.py
    
    # Generate sample data
    docker-compose exec backend python generate_sample_data.py
    
    print_success "Database initialized with sample data"
}

# Run end-to-end tests
run_tests() {
    print_status "Running end-to-end tests..."
    
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "✓ Backend health check passed"
    else
        print_error "✗ Backend health check failed"
        return 1
    fi
    
    # Test frontend
    if curl -f http://localhost/ &> /dev/null; then
        print_success "✓ Frontend health check passed"
    else
        print_error "✗ Frontend health check failed"
        return 1
    fi
    
    # Test API endpoints
    if curl -f http://localhost:8000/api/fraud-heatmap &> /dev/null; then
        print_success "✓ Heatmap API endpoint accessible"
    else
        print_warning "⚠ Heatmap API endpoint test failed (may need sample data)"
    fi
    
    print_success "Basic tests completed"
}

# Display deployment summary
show_summary() {
    echo ""
    echo "🎉 IRIS RegTech Platform Deployed Successfully!"
    echo "=============================================="
    echo ""
    echo "📊 Access Points:"
    echo "  • Frontend Application: http://localhost"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Interactive API: http://localhost:8000/redoc"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Update services: docker-compose up --build -d"
    echo ""
    echo "📋 Demo Features Available:"
    echo "  ✓ Investment tip risk analysis"
    echo "  ✓ Financial advisor verification"
    echo "  ✓ PDF document authenticity checking"
    echo "  ✓ Regulatory fraud monitoring dashboard"
    echo "  ✓ AI-powered risk forecasting"
    echo "  ✓ Fraud chain visualization"
    echo "  ✓ Human-in-the-loop review system"
    echo "  ✓ Real-time multi-source data integration"
    echo ""
    echo "🎯 Ready for demo! Follow the demo script at:"
    echo "   backend/demo_script.md"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "Cleaning up deployment..."
    docker-compose down --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "deploy")
            check_docker
            create_directories
            setup_environment
            deploy_services
            wait_for_services
            initialize_database
            run_tests
            show_summary
            ;;
        "test")
            print_status "Running tests only..."
            run_tests
            ;;
        "cleanup")
            cleanup
            ;;
        "restart")
            print_status "Restarting services..."
            docker-compose restart
            wait_for_services
            print_success "Services restarted"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            docker-compose ps
            ;;
        *)
            echo "Usage: $0 [deploy|test|cleanup|restart|logs|status]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  test     - Run tests only"
            echo "  cleanup  - Stop and clean up"
            echo "  restart  - Restart services"
            echo "  logs     - Show service logs"
            echo "  status   - Show service status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
