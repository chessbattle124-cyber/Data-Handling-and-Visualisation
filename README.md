# NIRF AI CHATBOT

An intelligent conversational analytics platform for exploring and querying India's **National Institutional Ranking Framework (NIRF)** data from **2017 to 2025**.

Ask natural language questions about college and university rankings, track institutional performance over time, compare states, and view dynamic analytical charts and data tables instantly.

---

## What is NIRF AI CHATBOT?

**NIRF AI CHATBOT** is an interactive, data-driven assistant designed to make higher education rankings accessible and easy to analyze. Instead of manually combing through dense ranking tables or spreadsheets, you can ask plain-English questions and get instant, accurate answers backed by interactive charts.

### Key Capabilities
- **Natural Language Understanding**: Ask questions in plain English—from simple queries ("Top 10 Engineering 2025") to complex trend analyses ("Which institutions improved most from 2017 to 2025?").
- **Hybrid Analytical Engine**: Combines deterministic Python/Pandas data processing for 100% accurate rankings with Google Gemini AI for flexible query interpretation and natural language responses.
- **Dynamic Data Visualizations**: Automatically generates relevant charts (bar charts, line trends, scatter plots via Chart.js) and summary data tables.
- **9-Year Historical Depth**: Covers 2017 through 2025 across all official NIRF categories.

---

## Dataset Overview

The chatbot queries a comprehensive, verified NIRF dataset containing:
- **6,844 records** across **9 years** (2017–2025)
- **13 Categories**: Engineering, Management, Medical, University, Overall, Pharmacy, College, Law, Architecture, Dental, Agriculture, Innovation, Research
- **2,149 unique institutions** across **34 Indian States & Union Territories**
- Metrics: Ranks, Overall Scores, Year-over-Year rank changes, and State/City distributions
---

## Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.

### 1. Installation & Environment Setup

Open Terminal in the project root directory:

```bash
# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. (Optional) Configure Gemini API Key

The chatbot includes a built-in deterministic query engine, but you can enable enhanced AI responses by configuring a Google Gemini API key:

```bash
cp .env.example .env
```
---

## How to Start the Application

You can start the server and frontend using either the **single-command script** or by running the services **manually in separate terminals**.

### Option A: Quick Start (Single Command)

Run the included startup script:

```bash
./start_chatbot.sh
```

This launches both the backend server and the frontend web server in the background:
- **Web UI**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Backend Health Check**: [http://127.0.0.1:5050/health](http://127.0.0.1:5050/health)

To stop all running servers:
```bash
./stop_chatbot.sh
```

---

### Option B: Manual Start (Two Terminals)

If you prefer to run and view logs in your terminal windows:

#### Terminal 1 — Start the Backend Server
```bash
source .venv/bin/activate
python3 backend/app.py
```
*The backend API server will start at `http://127.0.0.1:5050` (or `http://127.0.0.1:5000` if port 5050 is busy).*

#### Terminal 2 — Start the Frontend
```bash
python3 -m http.server 8000 --directory frontend
```
*The frontend web server will start at `http://localhost:8000`.*

Now open **[http://localhost:8000](http://localhost:8000)** in any web browser to use the chatbot.
