#!/bin/bash
# Stop NIRF chatbot servers

echo "Stopping NIRF chatbot servers..."
pkill -f "python.*backend/app.py" 2>/dev/null
pkill -f "python.*http.server.*tableau_extension" 2>/dev/null
echo "Done. All NIRF chatbot servers stopped."

