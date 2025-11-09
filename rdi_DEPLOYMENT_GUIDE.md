# 🚀 RDI Dashboard - Complete Deployment Guide

## From Zero to Live in 10 Minutes

---

## 📦 Step 1: Download Package

Download the entire **RDI_DASHBOARD** folder containing:

```
✅ app.py
✅ rdi_dashboard_engine.py
✅ rdi_config.json
✅ requirements.txt
✅ Procfile
✅ render.yaml
✅ .gitignore
✅ README.md
✅ DEPLOYMENT_GUIDE.md (this file)
```

---

## 💻 Step 2: Setup Locally

```bash
# Create project folder
mkdir ~/Downloads/rdi-dashboard
cd ~/Downloads/rdi-dashboard

# Copy all files from RDI_DASHBOARD here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Step 3: Test Locally (Optional)

```bash
# Run the application
python app.py

# Should see:
# ============================================================
# Starting RDI Dashboard - Research & Data Insights Platform
# ============================================================
# Starting Flask server on port 8080
```

Open browser: `http://localhost:8080`

Press `Ctrl+C` to stop.

---

## 📤 Step 4: Deploy to GitHub

### Initialize Git Repository

```bash
cd ~/Downloads/rdi-dashboard

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial RDI Dashboard deployment

- Complete data quality monitoring system
- Real-time GPS mapping
- Enumerator performance tracking
- Auto-refresh every hour
- Duration in minutes
- District-level insights
- Excel export functionality"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/rdi-dashboard.git

# Push to GitHub
git push -u origin main
```

**Credentials if prompted:**
- Username: Your GitHub username
- Password: Your Personal Access Token

---

## 🌐 Step 5: Deploy to Render.com

### Method 1: Automatic (Recommended)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select **"rdi-dashboard"** repository
5. Render auto-detects settings from `render.yaml`
6. Click **"Create Web Service"**

**Settings Auto-Applied:**
- Name: `rdi-dashboard`
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

### Method 2: Manual Configuration

If auto-detection doesn't work:

1. **Name:** `rdi-dashboard`
2. **Environment:** Python 3
3. **Build Command:** 
   ```
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```
   gunicorn app:app
   ```
5. **Branch:** `main`

---

## ⏳ Step 6: Monitor Deployment

Watch the deployment logs in Render:

**Expected Output:**
```
✓ Building...
✓ Installing dependencies from requirements.txt
✓ Starting service...
✓ Fetching data from API...
✓ Fetched 123 total records
✓ Filtered out 28 records before 2025-11-01
✓ Keeping 95 records from 2025-11-01 onwards
✓ Converted duration from seconds to minutes
✓ Split GPS coordinates from geopoint
✓ Dashboard generated successfully
✓ Deploy succeeded
```

**Time:** 2-3 minutes

---

## ✅ Step 7: Verify Dashboard

Visit your live dashboard:
```
https://rdi-dashboard-XXXXX.onrender.com
```

(Replace XXXXX with your actual Render URL)

**You Should See:**
- ✅ "RDI Dashboard" header
- ✅ 8 interactive visualizations
- ✅ 95 records displayed
- ✅ 5 districts in charts
- ✅ GPS map with locations
- ✅ Enumerator performance table
- ✅ Last updated timestamp (top right)

---

## 📊 Expected Dashboard Metrics

### Data Summary:
- **Total Submissions:** 95
- **Pilot Records Filtered:** 28
- **Collection Period:** Nov 1, 2025 onwards
- **Districts:** 5 (Bosaso, Dhusamareb, Beletweyne, Baki, Gabiley)
- **Enumerators:** 34
- **Auto-Refresh:** Every hour

### Quality Metrics:
- Completion rates by district
- Duration distribution (in minutes)
- Missing data analysis
- GPS coordinate validation
- Enumerator error rates

---

## 🎯 Post-Deployment Checklist

- [ ] Dashboard loads without errors
- [ ] All 8 sections display correctly
- [ ] GPS map shows interview locations
- [ ] District names appear in charts
- [ ] Duration shows in minutes (not seconds)
- [ ] Enumerators listed in performance table
- [ ] Summary statistics are accurate
- [ ] Last updated time is recent
- [ ] Manual update button works
- [ ] Excel export downloads successfully

---

## 🔄 Regular Maintenance

### Automatic Updates
- Dashboard fetches new data **every hour**
- No manual intervention needed
- Check logs periodically

### Manual Update
```
https://YOUR-DASHBOARD-URL/update
```
Click "Update Dashboard Now"

### Check System Status
```
https://YOUR-DASHBOARD-URL/api/status
```
Returns JSON with system health

### Download Reports
```
https://YOUR-DASHBOARD-URL/download/report
```
Gets Excel file with all metrics

---

## 🛠️ Configuration Changes

### Update Start Date

Edit `rdi_config.json`:
```json
"start_date": "2025-12-01"
```

Deploy changes:
```bash
git add rdi_config.json
git commit -m "Update start date to Dec 1"
git push origin main
```

Render auto-deploys in 2-3 minutes.

### Change Duration Thresholds

```json
"min_duration": 45,
"max_duration": 90
```

### Add/Remove Districts

```json
"target_districts": [
    "New District 1",
    "New District 2",
    "New District 3"
]
```

### Update GPS Boundaries

```json
"target_boundaries": {
    "lat_min": -10.0,
    "lat_max": 15.0,
    "lon_min": 35.0,
    "lon_max": 50.0
}
```

---

## 🐛 Troubleshooting

### Dashboard Shows "No Data"

**Cause:** All data is before start_date

**Solution:**
1. Check `start_date` in `rdi_config.json`
2. Verify data collection started after this date
3. Check Render logs for "Keeping X records"

### "Dashboard Not Available" Error

**Cause:** Data fetch or generation failed

**Solution:**
1. Check Render logs for error messages
2. Verify API credentials in `app.py`
3. Test API connectivity:
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" API_URL
   ```

### GPS Map Empty

**Cause:** No latitude/longitude data

**Solution:**
1. Check `hh_geopoint` column has data
2. Verify format: "lat lon elevation accuracy"
3. Check logs for "Split GPS coordinates"

### Duration in Seconds Not Minutes

**Cause:** Duration conversion failed

**Solution:**
1. Check `_duration` column exists
2. Verify values are numeric
3. Look for "Converted duration" in logs

### Enumerator Tracking Not Working

**Cause:** Column name mismatch

**Solution:**
1. Check `enumerator_column` in `rdi_config.json`
2. Verify column has data
3. Update column mapping if needed

---

## 📝 Updating the Dashboard

### Code Changes

```bash
cd ~/Downloads/rdi-dashboard

# Make your changes
# Edit app.py, rdi_dashboard_engine.py, etc.

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

Render auto-deploys in 2-3 minutes.

### Dependency Changes

Edit `requirements.txt`, then:
```bash
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

---

## 🔐 Security Best Practices

### For Production:

1. **Use Environment Variables for API Token**

Edit `app.py`:
```python
API_TOKEN = os.environ.get('API_TOKEN', 'default_token')
```

Add to Render:
- Dashboard → Environment
- Add variable: `API_TOKEN`
- Value: Your actual token

2. **Enable HTTPS**
- Automatic on Render.com
- Enforced by default

3. **Add Authentication** (Optional)

Install Flask-Login:
```bash
pip install flask-login
```

Add login routes in `app.py`.

---

## 📊 Monitoring & Logs

### View Logs in Render

1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Monitor in real-time

### Key Log Messages

**Success:**
```
✓ Fetched X total records
✓ Keeping Y records from start_date onwards
✓ Dashboard generated successfully
```

**Errors:**
```
✗ API request failed: 401
✗ Error fetching data: Connection timeout
✗ Error generating dashboard: Column not found
```

---

## 🎉 Success Indicators

✅ Render shows "Live" status  
✅ Dashboard URL loads successfully  
✅ All visualizations display  
✅ Data metrics are correct  
✅ GPS map is populated  
✅ No errors in logs  
✅ Auto-refresh is working  
✅ Excel export functions  

---

## 📞 Support Resources

**Documentation:**
- README.md - Features and configuration
- This guide - Deployment instructions
- Render Docs - https://render.com/docs

**Troubleshooting:**
1. Check Render logs
2. Verify configuration
3. Test locally
4. Review error messages

**Common Solutions:**
- API token issues → Check credentials
- Column not found → Update mapping
- No data → Check start_date
- GPS issues → Verify column format

---

## 🎯 Your Dashboard is Ready!

**Live URL:** 
```
https://rdi-dashboard-XXXXX.onrender.com
```

**Features Working:**
- ✅ Real-time data from API
- ✅ 95 records (Nov 1+ only)
- ✅ 5 districts tracked
- ✅ 34 enumerators analyzed
- ✅ Duration in minutes
- ✅ GPS mapping enabled
- ✅ Auto-refresh (hourly)
- ✅ Excel export ready

---

## 🚀 Next Steps

1. **Share the URL** with your team
2. **Monitor data quality** daily
3. **Download reports** weekly
4. **Update configuration** as needed
5. **Scale up** if traffic increases

---

**Congratulations! Your RDI Dashboard is now live! 🎉**

**Need Help?**
- Check README.md
- Review Render logs
- Test locally first
- Verify configuration

---

**RDI Dashboard v1.0.0**  
**Deployment Complete** ✅  
**Status: Production Ready** 🚀
