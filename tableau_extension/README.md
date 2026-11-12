# Tableau chatbot extension

This is a Tableau Dashboard Extension manifest and web app. Add it to a Tableau dashboard using **Objects → Extension → My Extensions** and choose `nirf_ai_assistant.trex`.

For local demonstration:
1. Start the Flask backend from the project root: `python backend/app.py`
2. Start the extension web server: `python -m http.server 8000 --directory tableau_extension`
3. Open Tableau Desktop, create/open the dashboard, drag an Extension object, and select the `.trex` file.
4. If Tableau blocks the local extension, use Tableau's extension security / safe-list settings as appropriate for your installation. For classroom use on another computer, host the extension and API on HTTPS and update the URL in the manifest and `index.html`.

The extension is embedded as a dashboard object. It uses the prepared CSV via the backend and displays a chart in the extension panel. It does not require Streamlit.
