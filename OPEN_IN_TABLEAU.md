
# Open the NIRF project in Tableau Public (Mac)

## Why the previous workbook failed
The earlier `.twbx` was hand-authored with invalid Tableau workbook XML. Tableau's D2E8DA72 validation errors are caused by that file, not your dataset or Mac. Do not reopen the earlier `NIRF_Analytics_AI.twbx`.

## Create a valid workbook in Tableau Public
1. Open Tableau Public.
2. Choose **File → New**.
3. Under Connect, choose **Text File** and select `data/nirf_tableau.csv` from this extracted folder.
4. Open a worksheet. Tableau should show dimensions and measures from the CSV.
5. Create sheets and a dashboard using `docs/TABLEAU_BUILD_GUIDE.md`.
6. Save from Tableau as `NIRF_Analytics_Dashboard.twbx`. This workbook is created by Tableau itself, so its XML structure is valid for your installed version.

## Add the chatbot inside the Tableau dashboard
1. Start the chatbot servers using the one-click script:
   ```bash
   ./start_chatbot.sh
   ```
   *(Or run manually in two terminal windows: `python3 backend/app.py` on port 5050 and `python3 -m http.server 8000 --directory tableau_extension` on port 8000).*

2. In Tableau, open your dashboard. From **Objects**, drag **Extension** into the dashboard.
3. Choose **My Extensions** / **Access Local Extensions** (wording depends on Tableau Public version), then select `tableau_extension/nirf_ai_assistant.trex`.
4. Approve the extension prompt if Tableau asks.
5. Save the workbook.

The chatbot is a dashboard extension object and therefore appears inside the Tableau dashboard. The local backend and extension web server must remain running while you demonstrate it. For another computer, localhost will not work; deploy the backend and extension to HTTPS and change the URL in the `.trex` and HTML.

## Dataset scope
The uploaded file contains 6,844 rows, 2017–2025, 13 categories, institution identity, state/city, overall score and numeric rank. It does not include TLR, RPC, GO, OI or Perception parameter scores. The chatbot explicitly reports that those parameter-specific analyses need the missing parameter dataset.
