#!/bin/bash

# =============================================================================
# Docker & Docker Compose Version Checker and Updater
# Victorian Monkey - victorianmonkey.org
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Required versions
MIN_DOCKER_VERSION="20.10.0"
MIN_COMPOSE_VERSION="2.0.0"

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

# Version comparison function
version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

# Check Docker installation
check_docker() {
    print_header "Checking Docker"

    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        print_success "Docker is installed: $DOCKER_VERSION"

        if version_gt "$MIN_DOCKER_VERSION" "$DOCKER_VERSION"; then
            print_error "Docker version $DOCKER_VERSION is too old!"
            print_warning "Minimum required: $MIN_DOCKER_VERSION"
            DOCKER_NEEDS_UPDATE=true
        else
            print_success "Docker version is compatible"
            DOCKER_NEEDS_UPDATE=false
        fi

        # Check Docker daemon
        if docker