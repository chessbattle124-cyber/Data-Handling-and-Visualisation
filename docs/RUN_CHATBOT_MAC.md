# Run chatbot on macOS

Open two Terminal windows in the extracted project folder.

**Window 1**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

**Window 2**
```bash
python3 -m http.server 8000 --directory tableau_extension
```

Health check: open `http://127.0.0.1:5050/health` (or `http://127.0.0.1:5000/health`).

Then open the TWBX in Tableau Desktop. The chatbot worksheet loads from `http://localhost:8000/index.html` and automatically detects and connects to the API on port 5050 (or 5000).
