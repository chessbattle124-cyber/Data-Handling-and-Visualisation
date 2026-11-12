# NIRF Analytics & AI — Tableau project

This package uses the **user-supplied `nirf_cleaned.csv`** as its only ranking data source. It includes a Tableau workbook package, an embedded Tableau dashboard extension for the chatbot, analysis-ready data, derived summaries, and a local query API.

## Dataset audit
- **6,844 source rows**
- **2017–2025** (nine years)
- **13 categories in this supplied file:** Agriculture, Architecture, College, Dental, Engineering, Innovation, Law, Management, Medical, Overall, Pharmacy, Research, University
- **2,149 distinct institution IDs**
- **34 state/UT labels**
- **0 duplicate Year + Category + Institution_ID keys**
- **2 withdrawn rows**
- **21 missing overall scores**
- **2 missing numeric ranks**

See `docs/DATA_AUDIT.md` and `data/data_quality_report.json`.

## Main Tableau deliverables
- `NIRF_Analytics_AI.twbx` — packaged Tableau workbook with CSV data included.
- `NIRF_Analytics_AI.twb` — editable workbook XML.
- `tableau_extension/nirf_ai_assistant.trex` — Tableau dashboard extension manifest.
- `tableau_extension/index.html` — chatbot UI embedded as a Tableau extension worksheet.
- `backend/app.py` — query API; uses Python standard library HTTP server plus Pandas/NumPy.

The workbook includes a dashboard with trend, institution comparison, top-100 state, category coverage, and the chatbot extension panel. Tableau may prompt you to trust/allow the local extension.

## Run on macOS
Open Terminal in this extracted project folder.

### Terminal 1 — chatbot API
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```
The API listens on `http://127.0.0.1:5000`.

### Terminal 2 — extension web server
```bash
python3 -m http.server 8000 --directory tableau_extension
```
The extension UI is served from `http://localhost:8000/index.html`.

### Open Tableau
1. Open `NIRF_Analytics_AI.twbx` in Tableau Desktop.
2. Open the dashboard **NIRF Analytics & AI**.
3. Ensure the two local services above are running; the chatbot panel is configured to use them.
4. If Tableau shows an extension security prompt, review and allow the local extension for this demonstration.
5. Use dashboard filters / worksheet filters in Tableau to explore Year, Category, State and Institution. For global dashboard filters, add the fields from the Data pane to Filters on the relevant worksheets and choose **Apply to Worksheets → All Using This Data Source**.

For another computer, replace `localhost` in the extension and API configuration with a reachable HTTPS host and configure Tableau extension allow-list / network policy. The included local configuration is for same-machine classroom demonstration.

## Example chatbot questions
- `Top 10 Engineering 2025`
- `How has Miranda House ranking changed from 2017 to 2025?`
- `Which states have the most top 100 institutions in 2025?`
- `Which states improved their top 100 representation from 2017 to 2025?`
- `Compare Karnataka and Tamil Nadu in 2025`
- `What percentage of institutions fall into each score quartile in Overall 2025?`
- `Which institutions improved most from 2017 to 2025?`
- `Which institutions entered or exited the top 10 in 2025?`
- `How many institutions moved from 51–100 into top 50 in 2025?`
- `Which institutions have highest ranking volatility?`

## Important source limitation
The uploaded CSV contains **overall Score and Rank only**. It does not include TLR, RPC, GO, OI, or Perception parameter scores. Therefore **14 of the PDF's 40 sample questions cannot be calculated from this file** (all five bivariate parameter questions, all five five-parameter multivariate questions, one parameter-variability question, and three research/teaching parameter outlier questions). The chatbot explicitly reports this limitation rather than making up answers. See `docs/SAMPLE_QUESTION_COVERAGE.md`.

The supplied dataset has 13 observed categories; the dashboard reflects those categories and does not invent categories absent from the upload. Rankings are category-specific: compare rank values only within the same category. Institutions missing from one year may be entrants/exits in the supplied data, not necessarily first-ever or last-ever NIRF participants.
