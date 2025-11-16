#!/bin/bash

# =============================================================================
# Odoo Community Edition - Update Script
# Victorian Monkey - victorianmonkey.org
# =============================================================================
# Questo script aggiorna il progetto da Git e riavvia i servizi Docker
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check if git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed!"
        exit 1
    fi
}

# Check Docker Compose v2
check_docker_compose() {
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose v2 is not installed!"
        print_info "Install Docker Compose v2: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository!"
        print_info "Run 'git init' first or clone the repository"
        exit 1
    fi
}

# Show current status
show_status() {
    print_header "Current Status"

    echo -e "${CYAN}Current branch:${NC} $(git branch --show-current)"
    echo -e "${CYAN}Current commit:${NC} $(git log -1 --pretty=format:'%h - %s (%cr)')"
    echo ""

    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        print_warning "You have uncommitted changes:"
        git status -s
        echo ""
    else
        print_success "Working directory is clean"
    fi
}

# Backup current state
backup_config() {
    print_header "Backing Up Configuration"

    BACKUP_DIR="backups/pre-update-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup .env if exists
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/.env"
        print_success "Backed up .env"
    fi

    # Backup odoo.conf if exists
    if [ -f "config/odoo.conf" ]; then
        cp config/odoo.conf "$BACKUP_DIR/odoo.conf"
        print_success "Backed up odoo.conf"
    fi

    # Backup docker-compose.override.yml if exists
    if [ -f "docker-compose.override.yml" ]; then
        cp docker-compose.override.yml "$BACKUP_DIR/docker-compose.override.yml"
        print_success "Backed up docker-compose.override.yml"
    fi

    print_success "Configuration backed up to: $BACKUP_DIR"
}

# Stash local changes
stash_changes() {
    if [[ -n $(git status -s) ]]; then
        print_header "Stashing Local Changes"

        read -p "Do you want to stash your local changes? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Auto-stash before update $(date +%Y%m%d-%H%M%S)"
            print_success "Changes stashed"
            STASHED=true
        else
            print_warning "Proceeding without stashing. This may cause conflicts."
            STASHED=false
        fi
    else
        STASHED=false
    fi
}

# Pull latest changes
pull_changes() {
    print_header "Pulling Latest Changes from Git"

    CURRENT_BRANCH=$(git branch --show-current)
    print_info "Pulling from origin/$CURRENT_BRANCH..."

    if git pull origin "$CURRENT_BRANCH"; then
        print_success "Successfully pulled latest changes"

        # Show what changed
        echo ""
        print_info "Recent commits:"
        git log --oneline -5
        echo ""
    else
        print_error "Failed to pull changes!"
        print_warning "You may have merge conflicts"

        if [ "$STASHED" = true ]; then
            print_info "Your changes are stashed. Run 'git stash pop' after resolving conflicts."
        fi

        exit 1
    fi
}

# Check if configuration files need updates
check_config_updates() {
    print_header "Checking Configuration Updates"

    CONFIG_UPDATED=false

    # Check if .env.example changed
    if git diff HEAD@{1} HEAD -- .env.example &> /dev/null; then
        if git diff HEAD@{1} HEAD -- .env.example | grep -q "^+"; then
            print_warning ".env.example has been updated!"
            print_info "Review changes and update your .env file if needed:"
            print_info "  diff .env.example .env"
            CONFIG_UPDATED=true
        fi
    fi

    # Check if odoo.conf.example changed
    if git diff HEAD@{1} HEAD -- conf/odoo.conf.example &> /dev/null; then
        if git diff HEAD@{1} HEAD -- conf/odoo.conf.example | grep -q "^+"; then
            print_warning "conf/odoo.conf.example has been updated!"
            print_info "Review changes and update your config/odoo.conf file if needed:"
            print_info "  diff conf/odoo.conf.example config/odoo.conf"
            CONFIG_UPDATED=true
        fi
    fi

    # Check if docker-compose.yml changed
    if git diff HEAD@{1} HEAD -- docker-compose.yml &> /dev/null; then
        if git diff HEAD@{1} HEAD -- docker-compose.yml | grep -q "^+"; then
            print_warning "docker-compose.yml has been updated!"
            print_info "Service configuration may have changed"
            CONFIG_UPDATED=true
        fi
    fi

    if [ "$CONFIG_UPDATED" = false ]; then
        print_success "No configuration updates needed"
    else
        echo ""
        read -p "Press Enter to continue with Docker services restart..."
    fi
}

# Pull Docker images
pull_images() {
    print_header "Pulling Latest Docker Images"

    if docker compose pull; then
        print_success "Docker images updated"
    else
        print_warning "Failed to pull some images (continuing anyway)"
    fi
}

# Restart services
restart_services() {
    print_header "Restarting Docker Services"

    print_info "Stopping services..."
    if docker compose down; then
        print_success "Services stopped"
    else
        print_error "Failed to stop services!"
        exit 1
    fi

    echo ""
    print_info "Starting services..."
    if docker compose up -d; then
        print_success "Services started"
    else
        print_error "Failed to start services!"
        print_info "Check logs with: docker compose logs -f"
        exit 1
    fi

    echo ""
    print_info "Waiting for services to be ready..."
    sleep 5

    # Show status
    echo ""
    docker compose ps
}

# Show logs
show_logs() {
    print_header "Service Logs (last 20 lines)"

    docker compose logs --tail=20

    echo ""
    print_info "To follow logs in real-time, run:"
    echo "  ${GREEN}docker compose logs -f${NC}"
}

# Apply stashed changes
apply_stash() {
    if [ "$STASHED" = true ]; then
        print_header "Applying Stashed Changes"

        read -p "Do you want to apply your stashed changes now? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if git stash pop; then
                print_success "Stashed changes applied"
            else
                print_error "Failed to apply stashed changes"
                print_info "Run 'git stash pop' manually when ready"
            fi
        else
            print_info "Your changes are still stashed. Run 'git stash pop' when ready."
        fi
    fi
}

# Final summary
show_summary() {
    print_header "Update Summary"

    echo -e "${GREEN}✓ Git repository updated${NC}"
    echo -e "${GREEN}✓ Docker images pulled${NC}"
    echo -e "${GREEN}✓ Services restarted${NC}"
    echo ""

    print_info "Access your services:"
    echo "  • Odoo: ${CYAN}https://victorianmonkey.org${NC}"
    echo "  • Grafana: ${CYAN}https://grafana.victorianmonkey.org${NC}"
    echo "  • Prometheus: ${CYAN}https://prometheus.victorianmonkey.org${NC}"
    echo ""

    print_info "Useful commands:"
    echo "  • View logs: ${GREEN}docker compose logs -f odoo-web${NC}"
    echo "  • Check status: ${GREEN}docker compose ps${NC}"
    echo "  • Stop all: ${GREEN}docker compose down${NC}"
    echo ""

    print_success "Update completed successfully!"
}

# Update Odoo modules
update_odoo_modules() {
    print_header "Update Odoo Modules (Optional)"

    echo ""
    read -p "Do you want to update Odoo modules in the database? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter database name (or press Enter to skip): " DB_NAME

        if [ -n "$DB_NAME" ]; then
            print_info "Updating all modules in database: $DB_NAME"
            print_warning "This may take several minutes..."

            if docker compose exec -T odoo-web odoo -u all -d "$DB_NAME" --stop-after-init; then
                print_success "Modules updated successfully!"

                print_info "Restarting Odoo..."
                docker compose restart odoo-web odoo-cron

                sleep 3
                print_success "Odoo restarted"
            else
                print_error "Failed to update modules!"
                print_info "Check logs with: docker compose logs -f odoo-web"
            fi
        else
            print_info "Skipping module update"
        fi
    else
        print_info "Skipping module update"
    fi
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
   _   _           _       _
  | | | |_ __   __| | __ _| |_ ___
  | | | | '_ \ / _` |/ _` | __/ _ \
  | |_| | |_) | (_| | (_| | ||  __/
   \___/| .__/ \__,_|\__,_|\__\___|
        |_|
  Victorian Monkey - Odoo Update
EOF
    echo -e "${NC}"

    # Pre-flight checks
    check_git
    check_git_repo
    check_docker_compose

    # Show current status
    show_status

    # Confirm update
    echo ""
    read -p "Do you want to proceed with the update? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Update cancelled"
        exit 0
    fi

    # Backup configuration
    backup_config

    # Stash changes if any
    stash_changes

    # Pull latest changes
    pull_changes

    # Check for config updates
    check_config_updates

    # Pull Docker images
    pull_images

    # Restart services
    restart_services

    # Show logs
    show_logs

    # Apply stashed changes
    apply_stash

    # Update Odoo modules (optional)
    update_odoo_modules

    # Summary
    show_summary
}

# Handle Ctrl+C
trap 'echo -e "\n${RED}Update interrupted!${NC}"; exit 130' INT

# Run main function
main "$@"
