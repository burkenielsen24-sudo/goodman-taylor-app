# Goodman-Taylor Application Suite

Complete Streamlit-based application suite for investment management, client intake, and compliance.

## 🚀 Available Applications

### Core Applications

1. **Home Dashboard** (`app/home.py`)
   - Central launcher and system status
   - Quick access to all applications
   - System metrics and health checks

2. **Client Intake & Management** (`app/goodman_taylor_app.py`)
   - Client intake form with PII collection
   - Contact management and opt-in tracking
   - Design file uploads and gallery
   - Admin panel for maintenance

3. **Deal Pipeline** (`app/pipeline.py`)
   - Investment deal tracking
   - Stage management (Lead → Closed)
   - Tags and filtering (family-first, pet-care, active-lifestyle)
   - CSV export functionality

### Financial & Analytics

4. **Financial Modeling** (`app/financials.py`) ✨ NEW
   - NPV & IRR calculations
   - Cash flow analysis
   - Portfolio comparison
   - ROI metrics
   - CSV upload support

### Compliance & Enrichment

5. **Compliance & Sanctions Screening** (`app/compliance.py`) ✨ NEW
   - OFAC SDN list screening
   - Automated name matching
   - Clearance workflow
   - Audit logging
   - Manual review interface

6. **Data Enrichment** (`app/enrichment.py`) ✨ NEW
   - OpenCorporates integration
   - Company registration lookup
   - Currency conversion tools
   - Data quality scoring
   - Batch enrichment

## 📦 Installation

```powershell
# Install all dependencies
pip install -r app/requirements.txt

# Run preflight checks
.\run_preflight.ps1
```

## 🎯 Quick Start

### Option 1: Home Dashboard (Recommended)
```powershell
cd app
python -m streamlit run home.py
```
This launches the central dashboard with links to all other apps.

### Option 2: Individual Apps
```powershell
# Client management
python -m streamlit run app/goodman_taylor_app.py

# Deal pipeline
python -m streamlit run app/pipeline.py

# Financial modeling
python -m streamlit run app/financials.py --server.port 8502

# Compliance screening
python -m streamlit run app/compliance.py --server.port 8503

# Data enrichment
python -m streamlit run app/enrichment.py --server.port 8504
```

### Option 3: Run Multiple Apps
```powershell
# Terminal 1: Main app
python -m streamlit run app/goodman_taylor_app.py

# Terminal 2: Financials
python -m streamlit run app/financials.py --server.port 8502

# Terminal 3: Compliance
python -m streamlit run app/compliance.py --server.port 8503
```

## 🎨 Application Details

### Financial Modeling (`financials.py`)
**Features:**
- Quick calculator with manual cash flow input
- CSV file upload for batch analysis
- Multi-deal portfolio comparison
- NPV calculation with adjustable discount rates
- IRR computation (Newton-Raphson method)
- Discounted cash flow tables
- Export results to CSV

**Usage:**
```powershell
python -m streamlit run app/financials.py
```
Then adjust discount rate (default 10%) and enter cash flows.

**Data Format:**
CSV with columns: `period,cashflow`
```csv
period,cashflow
0,-50000
1,15000
2,20000
```

---

### Compliance & Sanctions (`compliance.py`)
**Features:**
- OFAC SDN list integration (live fetch)
- Automated screening of clients and deals
- Conservative substring matching
- Manual review and clearance workflow
- Audit log for compliance tracking
- Export findings to CSV

**Usage:**
```powershell
python -m streamlit run app/compliance.py
```

**Process:**
1. Load targets from `data/clients.csv` and `data/deal_pipeline.csv`
2. Click "Run OFAC Screening"
3. Review findings in Results tab
4. Clear false positives in Clearance tab
5. Download audit logs for records

**Note:** Requires `requests` library. Install with:
```powershell
pip install requests
```

---

### Data Enrichment (`enrichment.py`)
**Features:**
- OpenCorporates company lookup
- Company registration data (number, jurisdiction, incorporation date)
- Currency conversion (USD to local)
- Data quality scoring (0-100)
- Batch enrichment for all deals
- Single deal enrichment
- FX rate caching

**Usage:**
```powershell
python -m streamlit run app/enrichment.py
```

**Optional:** Set OpenCorporates API key for increased rate limits:
```powershell
$env:OPEN_CORPORATES_API_KEY = 'your-key-here'
python -m streamlit run app/enrichment.py
```

**Process:**
1. Review pipeline status in tab 1
2. Select enrichment mode (single/batch)
3. Choose data sources (OpenCorporates, Currency)
4. Run enrichment
5. Review data quality scores

**Outputs:**
- Enriched data saved to `data/deal_pipeline_enriched.csv`
- Additional columns: `company_number`, `jurisdiction_code`, `incorporation_date`, `registry_url`, `fx_rate_usd`, `ticket_local`

---

## 📊 Data Flow

```
Clients Input → clients.csv
                    ↓
            goodman_taylor_app.py
                    ↓
    [PII Storage & Management]
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
Deals Input → deal_pipeline.csv
        ↓
    pipeline.py
        ↓
    ┌───┴───┬──────────┬──────────┐
    ↓       ↓          ↓          ↓
enrichment compliance financials analytics
    ↓       ↓          ↓          ↓
enriched  sanctions  NPV/IRR    KPIs
data      report     models     reports
```

## 🔐 Security & Privacy

**PII Protection:**
- All data stored locally in `data/` folder
- No external transmission except API enrichment (opt-in)
- Use `tools/sanitize_clients.py` to pseudonymize
- Run `python overarching_security.py` for scans

**API Keys:**
Set as environment variables:
```powershell
$env:ADMIN_PASS = 'your-admin-password'
$env:OPEN_CORPORATES_API_KEY = 'your-oc-key'
```

**Compliance:**
- Sanctions screening uses public OFAC SDN data
- Results require manual review (false positives possible)
- Audit logs track all compliance actions
- Never use this as sole compliance mechanism - consult legal counsel

## 🛠️ Troubleshooting

**"requests library required"**
```powershell
pip install requests
```

**Port already in use**
```powershell
# Use different port
python -m streamlit run app/financials.py --server.port 8505
```

**CSV encoding errors**
Ensure CSV files are UTF-8 encoded.

**OpenCorporates rate limits**
- Free tier: ~500 requests/month
- Get API key at opencorporates.com for higher limits
- Use cached data option in enrichment app

## 📝 Development

**Add new application:**
1. Create new file in `app/` directory
2. Follow existing patterns (see `financials.py` as template)
3. Add launch command to `app/home.py`
4. Update this README

**Testing:**
```powershell
# Run tests
pytest

# Security scan
python overarching_security.py

# CSV repair
python repair_clients_csv.py
```

## 🎯 Roadmap

### In Progress
- [x] Financial modeling GUI
- [x] Sanctions screening GUI
- [x] Data enrichment GUI

### Planned
- [ ] Security monitor dashboard (PII scanner UI)
- [ ] Portfolio analytics (KPI tracking, charts)
- [ ] Document management (term sheets, uploads)
- [ ] API backend (REST endpoints)
- [ ] Mobile-responsive design
- [ ] Role-based access control

## 📚 Resources

- **Investment Playbook:** `INVESTMENT_PLAYBOOK.md`
- **Security Guidelines:** `SECURITY.md`
- **Finance Readiness:** `FINANCE_READINESS.md`
- **Main README:** `README.md`

## 🤝 Support

For issues or questions:
1. Check this README
2. Review `INVESTMENT_PLAYBOOK.md` for business logic
3. Run `python overarching_security.py` for data issues
4. Check application logs in terminal output

---

**Values:** Family-First · Pet-Friendly · Active-Lifestyle  
**Mission:** We love pets, support families, and champion active living
