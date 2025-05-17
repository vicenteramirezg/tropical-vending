#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Tropical Vending Development Server ===${NC}"
echo -e "${YELLOW}This script helps you run the application locally.${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3.9+ to continue.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js is not installed. Please install Node.js 16+ to continue.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}npm is not installed. Please install npm to continue.${NC}"
    exit 1
fi

# Function to setup and activate virtual environment
setup_venv() {
    echo -e "${BLUE}Setting up Python virtual environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}Virtual environment created${NC}"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python setup complete!${NC}"
}

# Function to run Django backend
run_backend() {
    echo -e "${BLUE}Starting Django backend server...${NC}"
    cd backend
    python manage.py migrate
    python manage.py runserver
}

# Function to setup and run frontend in development mode
run_frontend_dev() {
    echo -e "${BLUE}Starting Vue.js frontend development server...${NC}"
    cd frontend
    npm install
    npm run dev
}

# Function to build frontend for production and collect static files
build_frontend() {
    echo -e "${BLUE}Building Vue.js frontend...${NC}"
    cd frontend
    npm install
    npm run build
    
    echo -e "${BLUE}Collecting static files...${NC}"
    cd ../backend
    python manage.py collectstatic --noinput
    
    echo -e "${GREEN}Frontend build complete!${NC}"
}

# Show options
show_options() {
    echo "Choose an option:"
    echo "1) Run backend only (Django)"
    echo "2) Run frontend only (Vue development server with hot reload)"
    echo "3) Build frontend and run backend (Production-like setup)"
    echo "4) Run both frontend and backend (in separate terminals with tmux)"
    echo "q) Quit"
    echo ""
}

# Main script logic
setup_venv

# Check if tmux is installed (for option 4)
HAS_TMUX=false
if command -v tmux &> /dev/null; then
    HAS_TMUX=true
fi

show_options

read -p "Enter your choice: " choice

case $choice in
    1)
        run_backend
        ;;
    2)
        run_frontend_dev
        ;;
    3)
        build_frontend
        run_backend
        ;;
    4)
        if [ "$HAS_TMUX" = true ]; then
            echo -e "${BLUE}Starting both servers using tmux...${NC}"
            tmux new-session -d -s frontend "cd $(pwd) && ./dev-server.sh 2"
            tmux new-session -d -s backend "cd $(pwd) && ./dev-server.sh 1"
            echo -e "${GREEN}Servers started in tmux sessions.${NC}"
            echo -e "Use ${YELLOW}tmux attach -t frontend${NC} or ${YELLOW}tmux attach -t backend${NC} to view server output."
            echo -e "Press Ctrl+B then D to detach from a tmux session."
        else
            echo -e "${YELLOW}tmux is not installed. Please install tmux or run the servers in separate terminals manually.${NC}"
            echo -e "Terminal 1: ${YELLOW}./dev-server.sh 1${NC}"
            echo -e "Terminal 2: ${YELLOW}./dev-server.sh 2${NC}"
        fi
        ;;
    q)
        echo -e "${GREEN}Exiting.${NC}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Invalid option. Please try again.${NC}"
        ;;
esac 