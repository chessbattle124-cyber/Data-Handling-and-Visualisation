from pathlib import Path
import os, sys, re, json, time, urllib.request
import numpy as np
import pandas as pd
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "nirf_tableau.csv"

# Load .env file if present
ENV_FILE = ROOT / ".env"
if ENV_FILE.exists():
    try:
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

def get_api_key():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k and not k.startswith("AQ.") and not k.startswith("AIza"):
        k = "AQ." + k
    return k

MODELS = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]
UNRELATED_MSG = "This is not related to our dataset. Ask related to our dataset."

def load():
    d = pd.read_csv(CSV)
    d["Year"] = pd.to_numeric(d["Year"], errors="coerce")
    d["Rank_numeric"] = pd.to_numeric(d["Rank_numeric"], errors="coerce")
    d["Score"] = pd.to_numeric(d["Score"], errors="coerce")
    d["is_withdrawn"] = d["is_withdrawn"].fillna(False).astype(bool)
    return d

DF = load()
CATEGORIES = sorted(DF["Category"].dropna().unique().tolist(), key=len, reverse=True)
STATES = sorted(DF["State"].dropna().unique().tolist(), key=len, reverse=True)
CITIES = sorted(DF["City"].dropna().unique().tolist(), key=len, reverse=True)
INSTITUTIONS = sorted(DF["Institution"].dropna().unique().tolist(), key=len, reverse=True)

INST_LOOKUP = {}
for name in INSTITUTIONS:
    for part in re.split(r"[\s,\-\(\)]+", name.lower()):
        if len(part) >= 4 and part not in {
            "institute", "technology", "indian", "national", "college", "university",
            "sciences", "engineering", "management", "state", "higher", "education"
        }:
            INST_LOOKUP.setdefault(part, []).append(name)

UNRELATED_PATTERNS = [
    r"\bweather\b", r"\btemperature\b", r"\bforecast\b", r"\brain\b", r"\brainfall\b", r"\bclimate\b",
    r"\bcricket\b", r"\bfootball\b", r"\bsoccer\b", r"\bipl\b", r"\bworld cup\b", r"\bmatch score\b",
    r"\brecipe\b", r"\bcook\b", r"\bfood\b", r"\bmovie\b", r"\bsong\b", r"\bjoke\b", r"\bpoem\b",
    r"\bpresident\b", r"\bprime minister\b", r"\bpolitics\b", r"\belection\b",
    r"\bcrypto\b", r"\bbitcoin\b", r"\bstock price\b", r"\bcapital of\b", r"\bhow to\b"
]

DATASET_KEYWORDS = [
    "nirf", "rank", "ranking", "score", "institution", "college", "university",
    "engineering", "medical", "management", "pharmacy", "law", "architecture",
    "dental", "agriculture", "research", "innovation", "iit", "nit", "iim", "aiims",
    "iisc", "campus", "top 10", "top 50", "top 100", "top 5", "cutoff", "admission"
]

def chart(kind, title, labels=None, series=None, x="Institution", y="Value", points=None):
    o = {"type": kind, "title": title, "xLabel": x, "yLabel": y}
    if labels is not None: o["labels"] = [str(v) for v in labels]
    if series is not None: o["series"] = series
    if points is not None: o["points"] = points
    return o

def numfmt(v):
    return "N/A" if pd.isna(v) else f"{v:,.2f}"

def parse_years(q):
    return [int(x) for x in re.findall(r"\b(?:201[7-9]|202[0-5])\b", q)]

def is_unrelated(q):
    ql = q.lower()
    if any(re.search(pat, ql) for pat in UNRELATED_PATTERNS):
        if "weather" in ql or "temperature" in ql or "cricket" in ql or "recipe" in ql or "joke" in ql:
            return True
        if not any(k in ql for k in DATASET_KEYWORDS):
            return True
            
    has_dataset_term = (
        any(k in ql for k in DATASET_KEYWORDS) or
        any(re.search(r"\b" + re.escape(c.lower()) + r"s?\b", ql) for c in CATEGORIES) or
        any(re.search(r"\b" + re.escape(s.lower()) + r"\b", ql) for s in STATES) or
        any(int(y) in ql for y in range(2017, 2026))
    )
    if not has_dataset_term:
        general_starts = [
            "what is ", "who is ", "tell me ", "can you ", "how ", "where is ",
            "which is the largest", "which is the best country"
        ]
        if any(ql.startswith(gs) for gs in general_starts):
            return True
    return False

def unavailable_parameter(q):
    words = ["tlr", "rpc", "perception", "research score", "teaching score", "graduation outcome", "outreach", "inclusivity", "five parameters", "five nirf parameters", "parameter correlation"]
    return any(w in q.lower() for w in words)

def extract_dataset_slice(q):
    ql = q.lower()
    years = parse_years(q)
    cat = next((c for c in CATEGORIES if re.search(r"\b" + re.escape(c.lower()) + r"s?\b", ql)), None)
    states = [s for s in STATES if re.search(r"\b" + re.escape(s.lower()) + r"\b", ql)]
    cities = [c for c in CITIES if re.search(r"\b" + re.escape(c.lower()) + r"\b", ql)]
    
    # Institution matching
    found_insts = set()
    for full_name in INSTITUTIONS:
        fl = full_name.lower()
        if len(fl) > 5 and fl in ql:
            found_insts.add(full_name)
            if len(found_insts) >= 4:
                break
                
    if not found_insts:
        tokens = re.split(r"[\s,\-\(\)\?]+", ql)
        stopwords = {
            "what", "when", "where", "which", "score", "scores", "rank", "ranking",
            "ranks", "rankings", "year", "years", "best", "list", "show", "tell",
            "about", "with", "from", "into", "over", "time", "high", "highest",
            "category", "state", "city", "institutions", "institution", "college",
            "colleges", "university", "universities", "engineering", "medical"
        }
        for t in tokens:
            if len(t) >= 4 and t not in stopwords and t not in [s.lower() for s in states] and t not in [c.lower() for c in cities]:
                if t in INST_LOOKUP:
                    found_insts.update(INST_LOOKUP[t][:2])
                    if len(found_insts) >= 4:
                        break

    # If nothing relevant to NIRF / colleges / locations / years was found, do not force a random slice
    has_dataset_term = (
        bool(found_insts) or
        bool(cat) or
        bool(states) or
        bool(cities) or
        bool(years) or
        any(k in ql for k in DATASET_KEYWORDS)
    )
    if not has_dataset_term:
        return []

    sub = DF[~DF.is_withdrawn].copy()
    if found_insts:
        sub = sub[sub.Institution.isin(found_insts)]
        if cat: sub = sub[sub.Category.str.lower() == cat.lower()]
        if years: sub = sub[sub.Year.isin(years)]
    else:
        if cat: sub = sub[sub.Category.str.lower() == cat.lower()]
        if states: sub = sub[sub.State.isin(states)]
        elif cities: sub = sub[sub.City.isin(cities)]
        if years: sub = sub[sub.Year.isin(years)]
        else:
            if not any(w in ql for w in ["trend", "history", "all years", "over time", "changed"]):
                sub = sub[sub.Year == 2025]
                
    m = re.search(r"\btop\s*(\d{1,3})\b", ql)
    n = int(m.group(1)) if m else (10 if not found_insts and len(sub) > 20 else 25)
    n = min(n, 30)
    
    sub = sub.sort_values(by=["Rank_numeric", "Score"], ascending=[True, False]).head(n)
    cols = ["Year", "Category", "Institution", "Rank_display", "Score", "City", "State"]
    return sub[[c for c in cols if c in sub.columns]].to_dict(orient="records")

def query_gemini_ai(question, records):
    api_key = get_api_key()
    if not api_key:
        return None
        
    has_records = bool(records and len(records) > 0)
    context_str = json.dumps(records, default=str) if has_records else "No matching rows found in the local database slice."

    prompt = f"""You are an advanced Natural Language Processing (NLP) AI Assistant specializing in Indian Higher Education, NIRF (National Institutional Ranking Framework) rankings, and academic analytics.

DATA CONTEXT FROM LOCAL DATABASE (nirf_tableau.csv):
{context_str}

DATABASE SCOPE:
- 6,844 records across 2017–2025 across 13 Categories: Overall, Engineering, University, College, Management, Pharmacy, Medical, Architecture, Law, Dental, Research, Agriculture, Innovation.
- 2,149 distinct institutions across 34 States/UTs with Overall Score (0-100) and Rank.

NLP INSTRUCTIONS:
1. DATABASE-SPECIFIC QUESTIONS:
   - When the user asks about statistics, rankings, scores, or trends present in the dataset, prioritize the factual numbers and institutions from the Data Context. Include relevant charts and tables.

2. QUESTIONS NOT IN THE DATABASE / CONCEPTUAL & GENERAL KNOWLEDGE:
   - If the user asks questions that are NOT present in the database (e.g. NIRF parameter methodology such as TLR, RPC, GO, OI, Perception; admission criteria; college history; campus life; course advice; or general knowledge):
     Leverage your comprehensive NLP capabilities and general knowledge to provide a clear, accurate, and insightful response.
     You may clarify whether specific parameter breakdowns are absent from the local file if relevant to the question.

3. RESPONSE FORMAT (STRICT JSON):
   Return ONLY a valid JSON object matching this schema:
   {{
     "answer": "Detailed, articulate natural language response answering the question thoroughly.",
     "chart": {{
       "type": "bar" | "line" | "scatter",
       "title": "Descriptive chart title",
       "labels": ["Label 1", "Label 2", ...],
       "series": [{{"name": "Series Name", "values": [num1, num2, ...]}}],
       "xLabel": "X axis label",
       "yLabel": "Y axis label"
     }} or null,
     "table": [{{"col1": "val1", ...}}] or null
   }}
   - Provide a chart when visual comparison or trend is meaningful (otherwise null).
   - In table, include relevant records or comparison data (otherwise null).

User Question: {question}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    body = json.dumps(payload).encode("utf-8")

    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
                    text = re.sub(r"\s*```$", "", text)
                out = json.loads(text)
                if not out.get("table") and records and len(records) <= 20:
                    out["table"] = records
                return out
        except urllib.error.HTTPError as e:
            # 429: rate limit, 503: high demand, 404: model retired, 500/502/504: gateway
            continue
        except Exception:
            continue
    return None

def select(d, q):
    ql = q.lower()
    cats = sorted(d.Category.dropna().astype(str).unique(), key=len, reverse=True)
    cat = next((c for c in cats if c.lower() in ql), None)
    if cat: d = d[d.Category.str.lower() == cat.lower()]
    states = sorted(d.State.dropna().astype(str).unique(), key=len, reverse=True)
    state = next((s for s in states if s.lower() in ql), None)
    if state: d = d[d.State.str.lower() == state.lower()]
    years = parse_years(q)
    if years:
        if len(years) >= 2: d = d[d.Year.isin(years)]
        else: d = d[d.Year == years[0]]
    else:
        d = d[d.Year == 2025]
    return d, cat, state, years

def respond(question):
    d0 = DF
    q = question.strip()
    ql = q.lower()

    # 1. Check for specialized statistical queries designed for the dashboard
    d, cat, state, years = select(d0, q)
    d = d[~d.is_withdrawn]

    # States with most top-100 institutions
    if ("state" in ql or "states" in ql) and any(w in ql for w in ["most", "highest count", "maximum"]) and ("top 100" in ql or "top-100" in ql):
        cat0 = cat or "Overall"
        y = years[0] if years else 2025
        base = d0[(d0.Category == cat0) & (~d0.is_withdrawn) & (d0.Year == y) & (d0.Rank_numeric <= 100)]
        counts = base.groupby("State").Institution_ID.nunique().sort_values(ascending=False).head(15).reset_index()
        counts.columns = ["State", "Institutions"]
        top_state = counts.iloc[0]["State"] if len(counts) > 0 else "N/A"
        top_cnt = int(counts.iloc[0]["Institutions"]) if len(counts) > 0 else 0
        return {
            "answer": f"In {y} ({cat0}), {top_state} has the most top-100 institutions with {top_cnt} institutions, followed by {', '.join(counts['State'].iloc[1:4].tolist())}.",
            "chart": chart("bar", f"States with Most Top-100 Institutions ({cat0} {y})", counts["State"].tolist(), [{"name": "Institutions", "values": counts["Institutions"].tolist()}], "State", "Number of Institutions"),
            "table": counts.to_dict("records")
        }

    # State representation change between two selected years
    if ("state" in ql or "states" in ql) and any(w in ql for w in ["improved", "improvement", "representation"]) and not any(w in ql for w in ["newly appearing", "new institutions", "new entrants"]):
        cat0 = cat or "Overall"
        y0, y1 = (min(years), max(years)) if len(years) >= 2 else (2017, 2025)
        base = d0[(d0.Category == cat0) & (~d0.is_withdrawn) & d0.Rank_numeric.le(100)]
        c0 = base[base.Year == y0].groupby("State").Institution_ID.nunique().rename("Start")
        c1 = base[base.Year == y1].groupby("State").Institution_ID.nunique().rename("End")
        comp = pd.concat([c0, c1], axis=1).fillna(0).reset_index()
        comp["Change"] = comp["End"] - comp["Start"]
        comp = comp.sort_values("Change", ascending=False).head(20)
        return {"answer": f"Change in top-100 representation by state for {cat0}, {y0} to {y1}. Positive change means more distinct institutions in the top 100 in the later year.", "chart": chart("bar", f"Change in top-100 state representation: {cat0}", comp.State, [{"name": "Change in institutions", "values": comp.Change.tolist()}], "State", "Change in count"), "table": comp.to_dict("records")}

    # Score dispersion and median/IQR
    if any(w in ql for w in ["dispersed", "dispersion", "more spread", "standard deviation", "interquartile", "iqr"]):
        g = d0[(~d0.is_withdrawn) & d0.Score.notna()]
        if cat: g = g[g.Category == cat]
        if state: g = g[g.State == state]
        if years: g = g[g.Year.isin(years)]
        else: g = g[g.Year.between(2017, 2025)]
        s = g.groupby("Year").Score.agg(Mean="mean", Median="median", StdDev="std",
              Q1=lambda x: x.quantile(.25), Q3=lambda x: x.quantile(.75)).reset_index()
        s["IQR"] = s.Q3 - s.Q1
        if "interquartile" in ql or "iqr" in ql or "median" in ql:
            series = [{"name": "Median", "values": s.Median.fillna(0).tolist()},
                    {"name": "Q1", "values": s.Q1.fillna(0).tolist()},
                    {"name": "Q3", "values": s.Q3.fillna(0).tolist()}]
            title = "Median and interquartile range by year"
            ylab = "Score"
        else:
            series = [{"name": "Standard deviation", "values": s.StdDev.fillna(0).tolist()}]
            title = "Score dispersion by year"; ylab = "Standard deviation"
        return {"answer": "Year-wise score dispersion and quartiles. Missing scores are excluded. Differences in category coverage and participating institutions may affect comparability.", "chart": chart("line", title, s.Year, series, "Year", ylab), "table": s.to_dict("records")}

    # Rank volatility across years
    if "volatility" in ql or "ranking volatility" in ql:
        cat0 = cat or "Overall"
        g = d0[(d0.Category == cat0) & (~d0.is_withdrawn) & d0.Rank_numeric.notna()]
        v = g.groupby("Institution").agg(Years=("Year", "nunique"), Mean_Rank=("Rank_numeric", "mean"), Rank_Volatility=("Rank_numeric", "std")).reset_index()
        v = v[v.Years >= 3].sort_values("Rank_Volatility", ascending=False).head(20)
        return {"answer": f"Institutions with the largest standard deviation of rank in {cat0}, among institutions with at least three observed years. This is descriptive volatility, not a forecast.", "chart": chart("bar", "Highest ranking volatility", v.Institution, [{"name": "Rank standard deviation", "values": v.Rank_Volatility.fillna(0).tolist()}], "Institution", "Rank standard deviation"), "table": v.to_dict("records")}

    # Top 10 entry/exit transitions
    if ("entered" in ql or "exited" in ql) and "top 10" in ql:
        cat0 = cat or "Overall"
        y1 = max(years) if years else 2025
        y0 = y1 - 1
        g = d0[(d0.Category == cat0) & (~d0.is_withdrawn) & d0.Rank_numeric.notna()]
        top0 = set(g[(g.Year == y0) & (g.Rank_numeric <= 10)].Institution_ID)
        top1 = set(g[(g.Year == y1) & (g.Rank_numeric <= 10)].Institution_ID)
        ent = g[(g.Year == y1) & g.Institution_ID.isin(top1 - top0)]
        ex = g[(g.Year == y0) & g.Institution_ID.isin(top0 - top1)]
        rows = [{"Transition": "Entered top 10", "Institution": n} for n in ent.Institution.tolist()]
        rows += [{"Transition": "Exited top 10", "Institution": n} for n in ex.Institution.tolist()]
        counts = {"Entered top 10": len(top1 - top0), "Exited top 10": len(top0 - top1)}
        return {"answer": f"{cat0} top-10 changes from {y0} to {y1}: {counts['Entered top 10']} entered and {counts['Exited top 10']} exited.", "chart": chart("bar", "Top-10 entries and exits", list(counts), [{"name": "Institutions", "values": list(counts.values())}], "Transition", "Institution count"), "table": rows}

    # Promotions from 51-100 to top 50
    if ("51–100" in ql or "51-100" in ql or "51 to 100" in ql) and "top 50" in ql:
        cat0 = cat or "Overall"
        y1 = max(years) if years else 2025
        y0 = y1 - 1
        g = d0[(d0.Category == cat0) & (~d0.is_withdrawn) & d0.Rank_numeric.notna()]
        a = g[g.Year == y0][["Institution_ID", "Institution", "Rank_numeric"]].rename(columns={"Rank_numeric": "Old_Rank"})
        b = g[g.Year == y1][["Institution_ID", "Rank_numeric"]].rename(columns={"Rank_numeric": "New_Rank"})
        z = a.merge(b, on="Institution_ID")
        z = z[z.Old_Rank.between(51, 100) & z.New_Rank.le(50)].sort_values("New_Rank")
        return {"answer": f"{len(z)} institutions moved from ranks 51–100 into the top 50 in {cat0}, {y0} to {y1}.", "chart": chart("bar", "51–100 to top-50 promotions", z.Institution, [{"name": "New rank", "values": z.New_Rank.tolist()}], "Institution", "Rank in later year"), "table": z.to_dict("records")}

    # 4. Extract data slice and consult Gemini AI
    records = extract_dataset_slice(q)
    ai_result = query_gemini_ai(q, records)
    if ai_result:
        return ai_result

    # 5. Local fallback if AI service is temporarily unavailable
    if records:
        return {
            "answer": f"Found {len(records)} matching records in the dataset for '{question}'.",
            "chart": chart("bar", f"Results for: {q[:30]}", [r.get("Institution", "")[:20] for r in records[:10]], [{"name": "Score", "values": [r.get("Score", 0) for r in records[:10]]}], "Institution", "Score") if any(r.get("Score") for r in records) else None,
            "table": records
        }

    return {
        "answer": f"I processed your query: '{question}'. This question is outside the local 2017–2025 ranking table and the online NLP model is currently unreachable. Please check your network connection and try again.",
        "chart": None,
        "table": None
    }

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, {"status": "ok", "dataset_loaded": CSV.exists(), "dataset": "nirf_tableau.csv"})
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if not self.path.startswith("/ask"):
            self._send(404, {"error": "Not found"})
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(n) or b"{}")
            q = str(payload.get("question", "")).strip()
            if not q:
                self._send(400, {"error": "Enter a question."})
                return
            self._send(200, respond(q))
        except Exception as e:
            self._send(500, {"answer": "The request could not be processed.", "error": str(e), "chart": None})

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    for port in [5050, 5000, 5001]:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            print(f"NIRF chatbot API running at http://127.0.0.1:{port}")
            server.serve_forever()
            break
        except OSError as e:
            if getattr(e, 'errno', None) in (48, 98):
                print(f"Port {port} in use, trying next port...")
                continue
            raise
