#!/bin/bash

# =============================================================================
# Odoo Community Production Setup Script
# Victorian Monkey - victorianmonkey.org
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root!"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed: $(docker --version)"
    else
        print_error "Docker is not installed!"
        echo "Install Docker: https://docs.docker.com/engine/install/"
        exit 1
    fi

    # Check Docker Compose
    if docker compose version &> /dev/null; then
        print_success "Docker Compose is installed: $(docker compose version)"
    else
        print_error "Docker Compose is not installed!"
        echo "Install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    # Check if user is in docker group
    if groups $USER | grep &>/dev/null '\bdocker\b'; then
        print_success "User is in docker group"
    else
        print_warning "User is not in docker group"
        print_info "Run: sudo usermod -aG docker $USER && newgrp docker"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Creating Directory Structure"

    directories=(
        "config"
        "data/filestore"
        "data/redis"
        "data/minio"
        "data/prometheus"
        "data/grafana"
        "data/n8n"
        "data/ollama"
        "data/ollama-webui"
        "traefik"
        "monitoring"
        "addons"
        "backups"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_info "Directory already exists: $dir"
        fi
    done

    # Fix permissions for service-specific directories
    print_info "Setting correct permissions for data directories..."

    # Odoo (runs as odoo:odoo - 101:101)
    if [ -d "data/filestore" ]; then
        sudo chown -R 101:101 data/filestore
        sudo chmod -R 755 data/filestore
        print_success "Odoo filestore permissions set"
    fi

    # Prometheus (runs as nobody:nobody - 65534:65534)
    if [ -d "data/prometheus" ]; then
        sudo chown -R 65534:65534 data/prometheus
        sudo chmod -R 755 data/prometheus
        print_success "Prometheus permissions set"
    fi

    # Grafana (runs as grafana:grafana - 472:472)
    if [ -d "data/grafana" ]; then
        sudo chown -R 472:472 data/grafana
        sudo chmod -R 755 data/grafana
        print_success "Grafana permissions set"
    fi

    # n8n (runs as node:node - 1000:1000)
    if [ -d "data/n8n" ]; then
        sudo chown -R 1000:1000 data/n8n
        sudo chmod -R 755 data/n8n
        print_success "n8n permissions set"
    fi

    # Ollama (runs as user - 1000:1000)
    if [ -d "data/ollama" ]; then
        sudo chown -R 1000:1000 data/ollama
        sudo chmod -R 755 data/ollama
        print_success "Ollama permissions set"
    fi

    # Ollama WebUI (runs as user - 1000:1000)
    if [ -d "data/ollama-webui" ]; then
        sudo chown -R 1000:1000 data/ollama-webui
        sudo chmod -R 755 data/ollama-webui
        print_success "Ollama WebUI permissions set"
    fi
}

# Setup Traefik
setup_traefik() {
    print_header "Setting up Traefik"

    # Create acme.json with correct permissions
    if [ ! -f "traefik/acme.json" ]; then
        touch traefik/acme.json
        chmod 600 traefik/acme.json
        print_success "Created traefik/acme.json with chmod 600"
    else
        chmod 600 traefik/acme.json
        print_info "traefik/acme.json already exists, permissions updated"
    fi

    # Check dynamic.yml
    if [ ! -f "traefik/dynamic.yml" ]; then
        print_error "traefik/dynamic.yml not found!"
        print_info "This file should exist. Check your repository."
        exit 1
    else
        print_success "traefik/dynamic.yml found"
    fi
}

# Setup configuration files
setup_config() {
    print_header "Setting up Configuration Files"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning ".env created from .env.example"
            print_warning "IMPORTANT: Edit .env with your actual credentials!"
            print_info "Run: nano .env"
        else
            print_error ".env.example not found!"
            exit 1
        fi
    else
        print_info ".env already exists"
    fi

    # Check if odoo.conf exists
    if [ ! -f "config/odoo.conf" ]; then
        if [ -f "conf/odoo.conf.example" ]; then
            cp conf/odoo.conf.example config/odoo.conf
            print_warning "config/odoo.conf created from example"
            print_warning "IMPORTANT: Edit config/odoo.conf with your settings!"
            print_info "Run: nano config/odoo.conf"
        else
            print_error "conf/odoo.conf.example not found!"
            exit 1
        fi
    else
        print_info "config/odoo.conf already exists"
    fi

    # Check prometheus.yml
    if [ ! -f "monitoring/prometheus.yml" ]; then
        print_error "monitoring/prometheus.yml not found!"
        print_info "This file should exist. Check your repository."
    else
        print_success "monitoring/prometheus.yml found"
    fi
}

# Generate htpasswd for BasicAuth
generate_passwords() {
    print_header "Generate BasicAuth Passwords"

    print_info "For Prometheus/Grafana BasicAuth, generate password with:"
    echo ""
    echo "  docker run --rm httpd:alpine htpasswd -nb admin yourpassword"
    echo ""
    print_info "Then update the hash in traefik/dynamic.yml"
    echo ""
}

# Check addons directory
check_addons() {
    print_header "Checking Custom Addons Directory"

    if [ -d "addons" ]; then
        print_success "Addons directory found"
        if [ -z "$(ls -A addons 2>/dev/null | grep -v README.md)" ]; then
            print_info "Addons directory is empty (ready for your custom modules)"
            print_info "See addons/README.md for development guide"
        else
            module_count=$(ls -1 addons | grep -v README.md | wc -l)
            print_info "Found $module_count custom modules"
        fi
    else
        print_warning "Addons directory not found"
    fi
}

# Set proper permissions
set_permissions() {
    print_header "Setting Permissions"

    # Odoo data directory - needs to be writable by container (UID 101 in odoo image)
    if [ -d "data/filestore" ]; then
        chmod -R 755 data/filestore
        print_success "Set permissions on data/filestore"
    fi

    # Redis data
    if [ -d "data/redis" ]; then
        chmod -R 755 data/redis
        print_success "Set permissions on data/redis"
    fi

    # MinIO data
    if [ -d "data/minio" ]; then
        chmod -R 755 data/minio
        print_success "Set permissions on data/minio"
    fi

    # Grafana data
    if [ -d "data/grafana" ]; then
        chmod -R 755 data/grafana
        print_success "Set permissions on data/grafana"
    fi

    # Prometheus data
    if [ -d "data/prometheus" ]; then
        chmod -R 755 data/prometheus
        print_success "Set permissions on data/prometheus"
    fi

    # Backups
    if [ -d "backups" ]; then
        chmod -R 755 backups
        print_success "Set permissions on backups"
    fi
}

# DNS Check
check_dns() {
    print_header "DNS Configuration Check"

    print_info "Verify your DNS records point to this server:"
    echo ""
    echo "  victorianmonkey.org              A    $(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
    echo "  www.victorianmonkey.org          A    $(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
    echo "  grafana.victorianmonkey.org      A    $(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
    echo "  prometheus.victorianmonkey.org   A    $(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
    echo ""

    print_info "Testing DNS resolution..."
    domains=("victorianmonkey.org" "www.victorianmonkey.org" "grafana.victorianmonkey.org" "prometheus.victorianmonkey.org")

    for domain in "${domains[@]}"; do
        if host "$domain" &>/dev/null; then
            ip=$(host "$domain" | grep "has address" | awk '{print $4}' | head -1)
            print_success "$domain resolves to $ip"
        else
            print_warning "$domain does not resolve yet"
        fi
    done
}

# Firewall check
check_firewall() {
    print_header "Firewall Configuration"

    if command -v ufw &> /dev/null; then
        print_info "UFW detected. Recommended rules:"
        echo ""
        echo "  sudo ufw allow 22/tcp   # SSH"
        echo "  sudo ufw allow 80/tcp   # HTTP"
        echo "  sudo ufw allow 443/tcp  # HTTPS"
        echo "  sudo ufw enable"
        echo ""

        if sudo ufw status | grep -q "Status: active"; then
            print_success "UFW is active"
            sudo ufw status numbered
        else
            print_warning "UFW is not active"
        fi
    else
        print_info "UFW not found. Make sure your firewall allows ports 22, 80, 443"
    fi
}

# Database connection test
test_database() {
    print_header "Database Connection Test"

    if [ -f ".env" ]; then
        source .env

        if [ -n "$HOST" ] && [ -n "$USER" ]; then
            print_info "Testing connection to database: $HOST"
            print_warning "This requires PostgreSQL client (psql) installed"

            read -p "Do you want to test database connection now? (y/N): " -n 1 -r
            echo

            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if command -v psql &> /dev/null; then
                    PGPASSWORD=$PASSWORD psql -h $HOST -p ${PORT:-5432} -U $USER -c "SELECT version();" && \
                        print_success "Database connection successful!" || \
                        print_error "Database connection failed!"
                else
                    print_warning "psql not installed. Install with: sudo apt install postgresql-client"
                fi
            fi
        else
            print_warning "Database credentials not found in .env"
        fi
    fi
}

# Final checklist
final_checklist() {
    print_header "Pre-Launch Checklist"

    echo "Before starting Docker Compose, ensure:"
    echo ""
    echo "  [  ] .env file is configured with real credentials"
    echo "  [  ] config/odoo.conf is configured"
    echo "  [  ] DNS records are pointing to this server"
    echo "  [  ] Firewall allows ports 80, 443, 22"
    echo "  [  ] External PostgreSQL database is accessible"
    echo "  [  ] BasicAuth passwords generated for Prometheus/Grafana"
    echo ""
}

# Show next steps
show_next_steps() {
    print_header "Next Steps"

    echo "1. Edit configuration files:"
    echo "   ${GREEN}nano .env${NC}"
    echo "   ${GREEN}nano config/odoo.conf${NC}"
    echo ""
    echo "2. Generate BasicAuth password (optional but recommended):"
    echo "   ${GREEN}docker run --rm httpd:alpine htpasswd -nb admin yourpassword${NC}"
    echo "   Then update traefik/dynamic.yml"
    echo ""
    echo "3. Start the stack:"
    echo "   ${GREEN}docker-compose up -d${NC}"
    echo ""
    echo "4. Watch the logs:"
    echo "   ${GREEN}docker-compose logs -f odoo-web${NC}"
    echo ""
    echo "5. Access Odoo:"
    echo "   ${GREEN}https://victorianmonkey.org${NC}"
    echo "   ${GREEN}https://www.victorianmonkey.org${NC}"
    echo ""
    echo "6. Access Monitoring:"
    echo "   ${GREEN}https://grafana.victorianmonkey.org${NC}"
    echo "   ${GREEN}https://prometheus.victorianmonkey.org${NC}"
    echo ""
    print_success "Setup script completed!"
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
   ___      _              _____                                      _ _
  / _ \  __| | ___   ___  / ____|___  _ __ ___  _ __ ___  _   _ _ __ (_) |_ _   _
 | | | |/ _` |/ _ \ / _ \| |   / _ \| '_ ` _ \| '_ ` _ \| | | | '_ \| | __| | | |
 | |_| | (_| | (_) | (_) | |__| (_) | | | | | | | | | | | |_| | | | | | |_| |_| |
  \___/ \__,_|\___/ \___/ \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|_|\__|\__, |
                                                                            |___/
  Victorian Monkey Production Setup
EOF
    echo -e "${NC}"

    check_root
    check_prerequisites
    create_directories
    setup_traefik
    setup_config
    check_addons
    set_permissions
    generate_passwords
    check_dns
    check_firewall
    test_database
    final_checklist
    show_next_steps
}

# Run main function
main "$@"
