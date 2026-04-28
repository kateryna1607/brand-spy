"""Luxury Web Interface for the Strategic Intelligence Agent."""
import os
import webbrowser
from flask import Flask, render_template, request, jsonify, send_from_directory
from agent.core import UniversalPriceAgent
from pathlib import Path
from dotenv import load_dotenv

# Load API Key
load_dotenv()

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')

# Ensure output directory exists
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    lang = data.get('lang', 'en')
    access_code = data.get('access_code')
    
    # Security check
    valid_code = os.environ.get('ACCESS_CODE', 'llh2026')
    if access_code != valid_code:
        return jsonify({
            'success': False,
            'error': 'INVALID EXECUTIVE ACCESS CODE. ACCESS DENIED.'
        }), 403

    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
    
    print(f"[DEBUG] Received analysis request for: {url} (Lang: {lang})", flush=True)
    try:
        print("[DEBUG] Initializing agent...", flush=True)
        agent = UniversalPriceAgent(dry_run=False)
        
        print(f"[DEBUG] Starting agent run for {url} in {lang}...", flush=True)
        report_path, error = agent.run(url, lang=lang)
        
        if error:
            print(f"[DEBUG] Agent returned error: {error}", flush=True)
            return jsonify({"success": False, "error": error}), 500

        print(f"[DEBUG] Analysis successful! Report at: {report_path}", flush=True)
        # Convert path to a URL relative to the server
        report_name = Path(report_path).name
        return jsonify({
            "success": True, 
            "report_url": f"/reports/{report_name}"
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[DEBUG] CRITICAL EXCEPTION in web_ui:\n{error_trace}", flush=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(OUTPUT_DIR, filename)

def start_ui():
    # Use environment variable for port (Cloud Run requirement)
    port = int(os.environ.get('PORT', 5001))
    
    # Only open browser if running locally (not in Docker/Cloud)
    if os.environ.get('KUBERNETES_SERVICE_HOST') is None and os.environ.get('PORT') is None:
        import threading
        import time
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f"http://127.0.0.1:{port}")
        threading.Thread(target=open_browser).start()
    
    # Run the server
    print(f" * BRAND SPY active on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    start_ui()
