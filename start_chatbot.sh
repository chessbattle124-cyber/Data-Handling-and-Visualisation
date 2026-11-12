#!/bin/bash
# Start both the backend API and extension UI servers

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Stopping any existing chatbot servers..."
pkill -f "python.*backend/app.py" 2>/dev/null
pkill -f "python.*http.server.*tableau_extension" 2>/dev/null
sleep 1

echo "Starting Backend API (port 5050)..."
python3 backend/app.py > /dev/null 2>&1 &

echo "Starting Extension Web Server (port 8000)..."
python3 -m http.server 8000 --directory tableau_extension > /dev/null 2>&1 &

sleep 2

echo "======================================================"
echo " NIRF AI Assistant is running!"
echo " • Web UI:       http://localhost:8000/index.html"
echo " • Backend API:  http://127.0.0.1:5050/health"
echo "======================================================"
echo "To stop both servers, run: ./stop_chatbot.sh"

