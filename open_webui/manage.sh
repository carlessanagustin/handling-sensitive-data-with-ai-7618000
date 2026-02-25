#!/bin/bash

# Open WebUI with SearXNG and Edge-TTS Management Script

set -e

show_help() {
    echo "Open WebUI Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services"
    echo "  stop      Stop all services"  
    echo "  restart   Restart all services"
    echo "  status    Show service status"
    echo "  logs      Show service logs"
    echo "  update    Update service images"
    echo "  clean     Clean up containers and volumes"
    echo "  help      Show this help message"
    echo ""
    echo "Services will be available at:"
    echo "  Open WebUI: http://localhost:3000"
    echo "  SearXNG:    http://localhost:4000"
    echo "  Edge-TTS:   http://localhost:5000"
}

start_services() {
    echo "🚀 Starting Open WebUI services..."
    docker-compose up -d
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Access your services:"
    echo "   Open WebUI: http://localhost:3000"
    echo "   SearXNG:    http://localhost:4000"  
    echo "   Edge-TTS:   http://localhost:5000"
    echo ""
    echo "📖 Check the README.md for more information"
}

stop_services() {
    echo "⏹️  Stopping Open WebUI services..."
    docker-compose down
    echo "✅ Services stopped successfully!"
}

restart_services() {
    echo "🔄 Restarting Open WebUI services..."
    docker-compose restart
    echo "✅ Services restarted successfully!"
}

show_status() {
    echo "📊 Service Status:"
    docker-compose ps
}

show_logs() {
    echo "📋 Recent logs (press Ctrl+C to exit):"
    docker-compose logs -f --tail=50
}

update_services() {
    echo "⬇️  Updating service images..."
    docker-compose pull
    echo "🔄 Restarting services with new images..."
    docker-compose up -d
    echo "✅ Services updated successfully!"
}

clean_services() {
    echo "🧹 Cleaning up containers and volumes..."
    echo "⚠️  This will remove all data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup completed!"
    else
        echo "❌ Cleanup cancelled"
    fi
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    update)
        update_services
        ;;
    clean)
        clean_services
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
