# 📊 RDI Dashboard
## Research & Data Insights Platform

**Complete data quality monitoring and analysis system built from scratch.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Features

### 📈 Real-Time Monitoring
- **Automatic Data Fetching** - Pulls from API every hour
- **Live Dashboard Updates** - Always shows current data
- **Custom Date Filtering** - Exclude pilot/test data
- **Smart Data Processing** - Automatic transformations

### 🗺️ Geographic Analysis
- **Interactive GPS Mapping** - See interview locations
- **District-Level Insights** - Completion by region
- **Boundary Validation** - Flag out-of-bounds coordinates
- **Duplicate Detection** - Identify suspicious GPS patterns

### ⏱️ Duration Analysis
- **Seconds to Minutes Conversion** - Human-readable times
- **Automatic Flagging** - Too short/long interviews
- **Trend Analysis** - Duration patterns over time
- **Enumerator Comparison** - Performance benchmarking

### 👥 Enumerator Tracking
- **Performance Metrics** - Error rates per person
- **Quality Scoring** - Duration, GPS, completion issues
- **Comparative Analysis** - Identify top/bottom performers
- **Missing Data Tracking** - By enumerator

### 📊 Data Quality
- **Completion Rates** - By district and overall
- **Missing Data Analysis** - Field-level insights
- **Logical Checks** - Data consistency validation
- **Quality Alerts** - Automatic threshold monitoring

### 📥 Export & Reporting
- **Excel Reports** - Comprehensive quality metrics
- **Chart Exports** - Publication-ready visualizations
- **API Access** - Programmatic data retrieval
- **Custom Reports** - Configurable metrics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager
- Git

### Installation

```bash
# Clone repository
cd ~/Downloads
mkdir rdi-dashboard
cd rdi-dashboard

# Copy all RDI_DASHBOARD files here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `rdi_config.json`:

```json
{
    "start_date": "2025-11-01",
    "min_duration": 30,
    "max_duration": 120,
    "target_districts": [
        "Your District 1",
        "Your District 2"
    ]
}
```

### Run Locally

```bash
python app.py
```

Open browser: `http://localhost:8080`

---

## 🌐 Deployment

### Deploy to Render.com

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial RDI Dashboard deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

2. **Connect to Render**
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your repository
- Render auto-detects settings from `render.yaml`

3. **Go Live**
- Deployment takes 2-3 minutes
- Dashboard automatically updates every hour

---

## 📊 Dashboard Sections

### 1. Completion Rates by District
Bar chart showing completion percentage for each district with target thresholds.

### 2. Interview Duration Distribution
Histogram showing duration patterns with automatic flagging of suspicious interviews.

### 3. Missing Data Analysis
Horizontal bar chart of top 10 fields with missing data, sorted by percentage.

### 4. Daily Submission Trends
Line chart tracking submissions over time to monitor collection progress.

### 5. Enumerator Error Rates
Ranked bar chart of enumerators by error rate, highlighting training needs.

### 6. Enumerator Performance Table
Detailed breakdown showing:
- Total interviews
- Duration issues
- GPS problems
- Completion rate
- Overall error percentage

### 7. GPS Coordinate Map
Interactive map with:
- All interview locations
- Color-coded by district
- Hover for enumerator details
- Zoom and pan capabilities

### 8. Summary Statistics
Key metrics dashboard showing:
- Total submissions
- Overall completion rate
- Quality flags count
- Collection period
- Average error rate

---

## ⚙️ Configuration Guide

### Basic Settings

```json
{
    "dashboard_name": "Your Dashboard Name",
    "version": "1.0.0",
    "start_date": "2025-11-01",
    "min_duration": 30,
    "max_duration": 120
}
```

### Column Mapping

Map your data columns to dashboard fields:

```json
{
    "column_mapping": {
        "district_column": "your_district_field",
        "duration_column": "duration_minutes",
        "enumerator_column": "your_enum_field",
        "geopoint_column": "your_gps_field"
    }
}
```

### Alert Thresholds

Set quality alert levels:

```json
{
    "alert_thresholds": {
        "min_completion_rate": 80,
        "max_missing_data_percent": 10,
        "max_duration_flags_percent": 5
    }
}
```

---

## 🔄 API Endpoints

### GET Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main dashboard |
| `/update` | Manual update page |
| `/api/status` | System status JSON |
| `/health` | Health check |
| `/download/report` | Excel report download |

### POST Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/update` | Trigger dashboard update |

---

## 📁 Project Structure

```
rdi-dashboard/
├── app.py                      # Flask application
├── rdi_dashboard_engine.py     # Visualization engine
├── rdi_config.json             # Configuration
├── requirements.txt            # Dependencies
├── Procfile                    # Deployment config
├── render.yaml                 # Render.com settings
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🛠️ Data Processing

### Automatic Transformations

**1. Date Filtering**
- Filters data from `start_date` onwards
- Timezone-aware comparison (UTC)
- Excludes pilot/test data

**2. Duration Conversion**
- Converts `_duration` (seconds) to minutes
- Creates `duration_minutes` column
- Flags <30min and >120min interviews

**3. GPS Splitting**
- Parses `hh_geopoint` field
- Extracts latitude and longitude
- Format: "lat lon elevation accuracy"

**4. Enumerator Analysis**
- Calculates error rates
- Tracks duration issues
- Monitors GPS quality
- Identifies completion problems

---

## 🎨 Customization

### Change Branding Colors

Edit `rdi_config.json`:

```json
{
    "branding": {
        "primary_color": "#667eea",
        "secondary_color": "#764ba2",
        "accent_color": "#06A77D",
        "logo_text": "Your Brand"
    }
}
```

### Add Custom Quality Checks

Edit `rdi_dashboard_engine.py`:

```python
def custom_quality_check(self):
    """Your custom validation logic"""
    # Add your code here
    return results
```

### Modify Auto-Refresh Interval

Edit `app.py`:

```python
REFRESH_INTERVAL = 3600  # Change to desired seconds
```

---

## 🐛 Troubleshooting

### Dashboard Shows No Data

**Check:**
1. Data collection started after `start_date`
2. API credentials are correct
3. `_submission_time` column exists
4. Network connectivity to API

**Solution:**
```bash
# Check logs
tail -f logs/rdi_dashboard.log

# Manual update
curl -X POST http://localhost:8080/api/update
```

### GPS Map Not Displaying

**Check:**
1. `hh_geopoint` column has data
2. Format: "latitude longitude elevation accuracy"
3. Coordinates within target boundaries

**Solution:**
```json
{
    "target_boundaries": {
        "lat_min": -5.0,
        "lat_max": 12.0,
        "lon_min": 40.0,
        "lon_max": 52.0
    }
}
```

### Duration Not Converting

**Check:**
1. `_duration` column exists
2. Values are in seconds (not minutes)
3. Column mapping is correct

**Solution:**
Verify in logs: "Converted duration from seconds to minutes"

---

## 📊 Performance

- **Data Processing**: ~2-5 seconds for 1000 records
- **Dashboard Generation**: ~10-15 seconds
- **Memory Usage**: ~200-500 MB
- **API Response Time**: <1 second

---

## 🔒 Security

- **API Tokens**: Stored in app.py (use environment variables in production)
- **CORS**: Enabled for web access
- **Rate Limiting**: Recommended for production
- **Authentication**: Add if needed for sensitive data

---

## 📝 License

MIT License - Free to use and modify

---

## 🤝 Support

**Issues:**
1. Check logs first
2. Verify configuration
3. Test locally
4. Check API connectivity

**Contact:**
- GitHub Issues
- Email Support
- Documentation

---

## 🎯 Current Features

**Data Processing:**
- ✅ 95 records (Nov 1+ only)
- ✅ 28 pilot records filtered
- ✅ 5 districts tracked
- ✅ 34 enumerators analyzed

**Dashboard:**
- ✅ 8 interactive visualizations
- ✅ Real-time GPS mapping
- ✅ Enumerator performance
- ✅ Quality metrics
- ✅ Auto-refresh (hourly)
- ✅ Excel export

---

## 🚀 Future Enhancements

- [ ] PDF report generation
- [ ] Email alerts
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Machine learning predictions
- [ ] Multi-language support

---

**Built with ❤️ for Research & Data Insights**

**Version:** 1.0.0  
**Last Updated:** November 2025  
**Status:** Production Ready ✅
