#!/bin/bash

# Script to help with qualtrics-util release management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}

# Function to check if there are uncommitted changes
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD --; then
        print_error "Working tree has uncommitted changes. Please commit or stash them first."
        exit 1
    fi
}

# Function to test the build locally
test_build() {
    print_status "Testing local build..."
    
    # Clean previous builds
    make clean
    
    # Test build
    make test-build
    
    # Test the executable
    if [ -f "dist/qualtrics-util" ]; then
        print_status "Testing executable..."
        ./dist/qualtrics-util --version
        print_status "Build test successful!"
    else
        print_error "Build test failed - executable not found"
        exit 1
    fi
}

# Function to create a release
create_release() {
    local version=$1
    
    if [ -z "$version" ]; then
        print_error "Version number required"
        echo "Usage: $0 release <version>"
        echo "Example: $0 release v0.8.24"
        exit 1
    fi
    
    # Validate version format
    if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Version must be in format vX.Y.Z (e.g., v0.8.24)"
        exit 1
    fi
    
    check_git_repo
    check_clean_working_tree
    
    print_status "Creating release $version..."
    
    # Update version in setup.py
    sed -i.bak "s/version=\"[^\"]*\"/version=\"${version#v}\"/" setup.py
    rm setup.py.bak
    
    # Commit version update
    git add setup.py
    git commit -m "Bump version to $version"
    
    # Create tag
    git tag -a "$version" -m "Release $version"
    
    # Push changes and tag
    git push origin main
    git push origin "$version"
    
    print_status "Release $version created and pushed!"
    print_status "GitHub Actions will now build the executables automatically."
    print_status "Check the Actions tab in your GitHub repository for build progress."
}

# Function to show help
show_help() {
    echo "qualtrics-util Release Helper"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  test        Test the build process locally"
    echo "  release     Create a new release"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test"
    echo "  $0 release v0.8.24"
}

# Main script logic
case "$1" in
    "test")
        test_build
        ;;
    "release")
        create_release "$2"
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
