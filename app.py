"""
RDI Dashboard - Research & Data Insights Platform
Complete data quality monitoring and analysis system
"""

from flask import Flask, render_template, jsonify, send_file, request
from flask_cors import CORS
import pandas as pd
import json
import os
import logging
from datetime import datetime
import requests
from rdi_dashboard_engine import RDIDashboardEngine
import threading
import time
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
API_URL = "https://api.ona.io/api/v1/data/864832"
API_TOKEN = "9cbc65f1c34ff5a3623cdac41043b788014992c0"
DATA_FILE = "rdi_data_export.csv"
DASHBOARD_FILE = "rdi_dashboard.html"
CONFIG_FILE = "rdi_config.json"
REFRESH_INTERVAL = 3600  # 1 hour

# Global variables
last_update_time = None
update_in_progress = False


def load_config():
    """Load RDI dashboard configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {CONFIG_FILE} not found, using defaults")
        return {
            'min_duration': 30,
            'max_duration': 120,
            'start_date': '2025-11-01',
            'required_fields': []
        }


def fetch_data():
    """Fetch latest data from API"""
    global last_update_time, update_in_progress
    
    try:
        update_in_progress = True
        logger.info("Fetching data from API...")
        
        headers = {"Authorization": f"Token {API_TOKEN}"}
        response = requests.get(API_URL, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            logger.info(f"Fetched {len(df)} total records")
            
            # Load configuration
            config = load_config()
            start_date_str = config.get('start_date', '2025-11-01')
            
            # Date filtering
            if '_submission_time' in df.columns:
                df['_submission_time'] = pd.to_datetime(df['_submission_time'])
                START_DATE = pd.to_datetime(start_date_str).tz_localize(pytz.UTC)
                
                original_count = len(df)
                df = df[df['_submission_time'] >= START_DATE]
                filtered_count = original_count - len(df)
                
                if filtered_count > 0:
                    logger.info(f"Filtered out {filtered_count} records before {start_date_str}")
                logger.info(f"Keeping {len(df)} records from {start_date_str} onwards")
            
            # Duration conversion (seconds to minutes)
            if '_duration' in df.columns:
                df['duration_minutes'] = df['_duration'] / 60
                logger.info("Converted duration from seconds to minutes")
            
            # GPS geopoint splitting
            if 'hh_geopoint' in df.columns:
                def split_geopoint(geopoint):
                    if pd.isna(geopoint) or geopoint == '':
                        return None, None
                    try:
                        parts = str(geopoint).split()
                        if len(parts) >= 2:
                            return float(parts[0]), float(parts[1])
                        return None, None
                    except:
                        return None, None
                
                df[['latitude', 'longitude']] = df['hh_geopoint'].apply(
                    lambda x: pd.Series(split_geopoint(x))
                )
                logger.info("Split GPS coordinates from geopoint")
            
            # Save processed data
            df.to_csv(DATA_FILE, index=False)
            last_update_time = datetime.now()
            logger.info(f"Successfully saved {len(df)} records")
            return True
        else:
            logger.error(f"API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        update_in_progress = False


def generate_dashboard():
    """Generate RDI dashboard"""
    try:
        logger.info("Generating RDI dashboard...")
        config = load_config()
        
        if not os.path.exists(DATA_FILE):
            logger.error(f"Data file {DATA_FILE} not found")
            return False
        
        # Check if data exists
        df = pd.read_csv(DATA_FILE)
        
        if len(df) == 0:
            logger.warning("No data available")
            # Create placeholder page
            placeholder_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>RDI Dashboard - Awaiting Data</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        border-radius: 20px;
                        padding: 60px 40px;
                        max-width: 800px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                    }
                    .logo { font-size: 72px; margin-bottom: 20px; }
                    h1 { color: #667eea; font-size: 36px; margin-bottom: 10px; }
                    h2 { color: #555; font-size: 24px; margin-bottom: 30px; font-weight: normal; }
                    .status-box {
                        background: #e8f4fd;
                        padding: 30px;
                        border-radius: 15px;
                        margin: 30px 0;
                        text-align: left;
                    }
                    .status-item {
                        display: flex;
                        justify-content: space-between;
                        padding: 12px 0;
                        border-bottom: 1px solid #d0e7f5;
                    }
                    .status-item:last-child { border-bottom: none; }
                    .status-label { font-weight: 600; color: #667eea; }
                    .status-value { color: #333; }
                    .note {
                        background: #fff3cd;
                        color: #856404;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        border-left: 4px solid #ffc107;
                    }
                    .features {
                        background: #f8f9fa;
                        padding: 25px;
                        border-radius: 10px;
                        margin: 20px 0;
                        text-align: left;
                    }
                    .features h3 { color: #667eea; margin-bottom: 15px; }
                    .features ul { list-style: none; padding-left: 0; }
                    .features li { padding: 8px 0; padding-left: 30px; position: relative; }
                    .features li:before {
                        content: "✓";
                        position: absolute;
                        left: 0;
                        color: #06A77D;
                        font-weight: bold;
                        font-size: 18px;
                    }
                    .actions {
                        margin-top: 30px;
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                        flex-wrap: wrap;
                    }
                    .btn {
                        padding: 15px 30px;
                        border-radius: 10px;
                        text-decoration: none;
                        font-weight: 600;
                        font-size: 16px;
                        transition: all 0.3s;
                        display: inline-block;
                    }
                    .btn-primary {
                        background: #667eea;
                        color: white;
                    }
                    .btn-primary:hover {
                        background: #5568d3;
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
                    }
                    .btn-secondary {
                        background: #06A77D;
                        color: white;
                    }
                    .btn-secondary:hover {
                        background: #059669;
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(6,167,125,0.4);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">📊</div>
                    <h1>RDI Dashboard</h1>
                    <h2>Research & Data Insights Platform</h2>
                    
                    <div class="status-box">
                        <div class="status-item">
                            <span class="status-label">Dashboard Status</span>
                            <span class="status-value">✅ Active & Ready</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Data Collection Start</span>
                            <span class="status-value">November 1, 2025</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Current Records</span>
                            <span class="status-value">0 (Awaiting Data)</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Auto-Refresh</span>
                            <span class="status-value">Every hour</span>
                        </div>
                    </div>
                    
                    <div class="note">
                        <strong>📌 Note:</strong> The dashboard will automatically populate once data collection 
                        begins on November 1, 2025. All data before this date is excluded from analysis.
                    </div>
                    
                    <div class="features">
                        <h3>Dashboard Features</h3>
                        <ul>
                            <li>Real-time completion rates by district</li>
                            <li>Interactive GPS location mapping</li>
                            <li>Interview duration analysis (in minutes)</li>
                            <li>Enumerator performance tracking</li>
                            <li>Data quality metrics & alerts</li>
                            <li>Missing data analysis</li>
                            <li>Excel report export</li>
                            <li>Automatic hourly updates</li>
                        </ul>
                    </div>
                    
                    <div class="actions">
                        <a href="/update" class="btn btn-primary">Check for New Data</a>
                        <a href="/api/status" class="btn btn-secondary">System Status</a>
                    </div>
                </div>
            </body>
            </html>
            """
            with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
                f.write(placeholder_html)
            logger.info("Created placeholder dashboard")
            return True
        
        # Generate actual dashboard
        dashboard = RDIDashboardEngine(DATA_FILE, config=config)
        
        # Get column mappings from config
        col_mapping = config.get('column_mapping', {})
        district_col = col_mapping.get('district_column', 'district')
        duration_col = col_mapping.get('duration_column', 'duration_minutes')
        enum_col = col_mapping.get('enumerator_column', 'enumerator_id')
        
        # Generate dashboard
        dashboard.generate_dashboard(
            output_file=DASHBOARD_FILE,
            district_column=district_col,
            duration_column=duration_col,
            lat_column='latitude',
            lon_column='longitude',
            enumerator_column=enum_col
        )
        
        logger.info("Dashboard generated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def update_dashboard():
    """Complete dashboard update workflow"""
    logger.info("Starting dashboard update...")
    
    if fetch_data():
        if generate_dashboard():
            logger.info("Dashboard update completed successfully")
            return True
    
    logger.error("Dashboard update failed")
    return False


def auto_refresh_worker():
    """Background worker for auto-refresh"""
    while True:
        try:
            logger.info("Auto-refresh triggered")
            update_dashboard()
            time.sleep(REFRESH_INTERVAL)
        except Exception as e:
            logger.error(f"Error in auto-refresh: {str(e)}")
            time.sleep(60)


@app.route('/')
def index():
    """Serve the main dashboard"""
    if not os.path.exists(DASHBOARD_FILE):
        if not update_dashboard():
            return """
            <html>
                <head><title>RDI Dashboard - Error</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>Dashboard Not Available</h1>
                    <p>Unable to generate dashboard. Please check logs.</p>
                    <p><a href="/update">Try updating</a></p>
                </body>
            </html>
            """, 500
    
    try:
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            dashboard_html = f.read()
        
        # Add update indicator
        update_info = f"""
        <div style="position: fixed; top: 10px; right: 10px; background: #667eea; color: white; 
                    padding: 12px 20px; border-radius: 8px; font-family: Arial; z-index: 9999; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <strong>RDI Dashboard</strong><br>
            Last Updated: {last_update_time.strftime('%Y-%m-%d %H:%M:%S') if last_update_time else 'Unknown'}<br>
            <small style="opacity: 0.9;">Auto-refreshes every hour</small>
        </div>
        """
        
        dashboard_html = dashboard_html.replace('<body>', f'<body>{update_info}')
        return dashboard_html
        
    except Exception as e:
        logger.error(f"Error serving dashboard: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500


@app.route('/api/status')
def status():
    """API endpoint for system status"""
    return jsonify({
        'status': 'online',
        'dashboard': 'RDI Dashboard - Research & Data Insights',
        'version': '1.0.0',
        'last_update': last_update_time.isoformat() if last_update_time else None,
        'update_in_progress': update_in_progress,
        'data_available': os.path.exists(DATA_FILE),
        'dashboard_available': os.path.exists(DASHBOARD_FILE)
    })


@app.route('/api/update', methods=['POST'])
def trigger_update():
    """Manually trigger dashboard update"""
    if update_in_progress:
        return jsonify({
            'success': False,
            'message': 'Update already in progress'
        }), 409
    
    thread = threading.Thread(target=update_dashboard)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Dashboard update triggered'
    })


@app.route('/update')
def update_page():
    """Manual update page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RDI Dashboard - Update</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 50px 40px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 { color: #667eea; font-size: 32px; margin-bottom: 10px; }
            p { color: #666; font-size: 16px; margin-bottom: 30px; line-height: 1.6; }
            .buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            button {
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102,126,234,0.4);
            }
            .btn-secondary {
                background: #06A77D;
                color: white;
            }
            .btn-secondary:hover {
                background: #059669;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(6,167,125,0.4);
            }
            #status {
                margin-top: 25px;
                padding: 20px;
                border-radius: 10px;
                display: none;
            }
            .success { background: #d4edda; color: #155724; display: block; }
            .error { background: #f8d7da; color: #721c24; display: block; }
            .info { background: #d1ecf1; color: #0c5460; display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔄 RDI Dashboard Update</h1>
            <p>Click the button below to fetch the latest data and refresh your dashboard.</p>
            <div class="buttons">
                <button onclick="updateDashboard()" class="btn-primary">Update Dashboard Now</button>
                <button onclick="goHome()" class="btn-secondary">View Dashboard</button>
            </div>
            <div id="status"></div>
        </div>
        
        <script>
            function updateDashboard() {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'info';
                statusDiv.innerHTML = '⏳ Updating dashboard... Please wait.';
                
                fetch('/api/update', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            statusDiv.className = 'success';
                            statusDiv.innerHTML = '✅ Dashboard update triggered! Redirecting...';
                            setTimeout(() => { window.location.href = '/'; }, 3000);
                        } else {
                            statusDiv.className = 'error';
                            statusDiv.innerHTML = '❌ Error: ' + data.message;
                        }
                    })
                    .catch(error => {
                        statusDiv.className = 'error';
                        statusDiv.innerHTML = '❌ Error: ' + error;
                    });
            }
            
            function goHome() {
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    """


@app.route('/download/report')
def download_report():
    """Download quality report"""
    try:
        report_file = 'rdi_quality_report.xlsx'
        
        if not os.path.exists(report_file):
            config = load_config()
            dashboard = RDIDashboardEngine(DATA_FILE, config=config)
            dashboard.export_quality_report(report_file)
        
        return send_file(report_file, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return f"Error generating report: {str(e)}", 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'dashboard': 'RDI Dashboard',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting RDI Dashboard - Research & Data Insights Platform")
    logger.info("=" * 60)
    
    # Initial dashboard generation
    if not os.path.exists(DASHBOARD_FILE):
        logger.info("Dashboard not found, generating initial dashboard...")
        update_dashboard()
    
    # Start auto-refresh worker
    refresh_thread = threading.Thread(target=auto_refresh_worker, daemon=True)
    refresh_thread.start()
    logger.info(f"Auto-refresh enabled (interval: {REFRESH_INTERVAL} seconds)")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask server on port {port}")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
