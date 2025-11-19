import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="Goodman-Taylor Dashboard", page_icon="🏡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .tagline {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .app-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        transition: all 0.3s;
    }
    .app-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .values-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏡 Goodman-Taylor Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Investment & Client Management Platform</div>', unsafe_allow_html=True)

# Values
st.markdown("""
<div class="values-box">
    <strong>Our Values:</strong> Family-First · Pet-Friendly · Active-Lifestyle<br>
    <em>We love pets, support families, and champion active living</em>
</div>
""", unsafe_allow_html=True)

# Navigation
st.markdown("## 📱 Applications")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👥 Client & Operations")
    
    with st.container():
        st.markdown("#### 📝 Client Intake & Dashboard")
        st.markdown("Manage client intake, contact info, and design uploads")
        if st.button("🚀 Launch Client App", key="client_app"):
            st.info("Run: `streamlit run app/goodman_taylor_app.py`")
            st.code("python -m streamlit run app/goodman_taylor_app.py", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 💼 Deal Pipeline")
        st.markdown("Track investment deals, stages, and closings")
        if st.button("🚀 Launch Pipeline", key="pipeline_app"):
            st.info("Run: `streamlit run app/pipeline.py`")
            st.code("python -m streamlit run app/pipeline.py", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 📁 Document Management")
        st.markdown("Manage term sheets, design gallery, and file uploads")
        if st.button("🚀 Launch Documents", key="docs_app"):
            st.info("Run: `streamlit run app/documents.py`")
            st.code("python -m streamlit run app/documents.py", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 📊 Portfolio Analytics")
        st.markdown("Impact KPIs, metrics, and LP reporting")
        st.caption("⚠️ Coming soon")

with col2:
    st.markdown("### 💰 Financial & Compliance")
    
    with st.container():
        st.markdown("#### 💵 Financial Modeling")
        st.markdown("NPV, IRR calculations, and ROI analysis")
        if st.button("🚀 Launch Financials", key="financials_app"):
            st.info("Run: `streamlit run app/financials.py`")
            st.code("python -m streamlit run app/financials.py --server.port 8502", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 🛡️ Compliance & Sanctions")
        st.markdown("OFAC screening, clearance workflow, audit logs")
        if st.button("🚀 Launch Compliance", key="compliance_app"):
            st.info("Run: `streamlit run app/compliance.py`")
            st.code("python -m streamlit run app/compliance.py --server.port 8503", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 🔍 Data Enrichment")
        st.markdown("OpenCorporates integration, FX rates, data quality")
        if st.button("🚀 Launch Enrichment", key="enrichment_app"):
            st.info("Run: `streamlit run app/enrichment.py`")
            st.code("python -m streamlit run app/enrichment.py --server.port 8504", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 🔒 Security Monitor")
        st.markdown("PII scanning, schema validation, data sanitization")
        if st.button("🚀 Launch Security", key="security_app"):
            st.info("Run: `streamlit run app/security.py`")
            st.code("python -m streamlit run app/security.py --server.port 8505", language="powershell")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 📈 Portfolio Analytics")
        st.markdown("Impact metrics, KPI tracking, LP reporting")
        if st.button("🚀 Launch Analytics", key="analytics_app"):
            st.info("Run: `streamlit run app/analytics.py`")
            st.code("python -m streamlit run app/analytics.py --server.port 8506", language="powershell")

# Additional Tools
st.markdown("---")
st.markdown("## 🔧 Tools & Utilities")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📋 CSV Repair")
    st.markdown("PII scan, schema validation, secrets detection")
    st.caption("⚠️ Coming soon")

with col2:
    st.markdown("#### 📄 Document Management")
    st.markdown("Term sheets, uploads, design gallery")
    st.caption("⚠️ Coming soon")

with col3:
    st.markdown("#### 🛠️ Admin Tools")
    st.markdown("CSV repair, data sanitization, backups")
    if st.button("Run Security Scan"):
        st.code("python overarching_security.py", language="powershell")
    if st.button("Repair Clients CSV"):
        st.code("python repair_clients_csv.py", language="powershell")

# Footer
st.markdown("---")
st.markdown("### 📚 Quick Start Guide")

with st.expander("🚀 How to run applications"):
    st.markdown("""
    **Option 1: Using this launcher**
    - Click any "Launch" button above to see the command
    - Copy and run the command in PowerShell
    
    **Option 2: Direct launch**
    ```powershell
    # Navigate to app directory
    cd app
    
    # Run any app
    python -m streamlit run <app_name>.py
    
    # Run on different ports (for multiple apps)
    python -m streamlit run financials.py --server.port 8502
    python -m streamlit run compliance.py --server.port 8503
    ```
    
    **Option 3: Use batch files**
    ```powershell
    # Main app
    .\\app\\run_app.bat
    
    # Or PowerShell script
    .\\app\\run_app.ps1
    ```
    """)

with st.expander("📦 Installation & Setup"):
    st.markdown("""
    **Install dependencies:**
    ```powershell
    pip install -r app/requirements.txt
    ```
    
    **Run preflight checks:**
    ```powershell
    .\\run_preflight.ps1
    ```
    
    **Environment variables (optional):**
    - `ADMIN_PASS` - Admin password for sensitive operations
    - `OPEN_CORPORATES_API_KEY` - For data enrichment (increases rate limits)
    """)

with st.expander("🔐 Security & Privacy"):
    st.markdown("""
    **Data Protection:**
    - All PII stored locally in `data/` folder
    - Use `.security-ignore` to whitelist test fixtures
    - Run `python overarching_security.py` for security scans
    - Use `python tools/sanitize_clients.py` to pseudonymize data
    
    **Best Practices:**
    - Never commit real client data to git
    - Use fixtures (`*_fixture.csv`) for testing
    - Review sanctions findings manually (false positives possible)
    - Keep API keys in environment variables, not code
    """)

# System Status
st.markdown("---")
st.markdown("### 📊 System Status")

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

col1, col2, col3, col4 = st.columns(4)

with col1:
    clients_file = DATA_DIR / "clients.csv"
    if clients_file.exists():
        import pandas as pd
        try:
            df = pd.read_csv(clients_file)
            st.metric("Clients", len(df))
        except:
            st.metric("Clients", "Error")
    else:
        st.metric("Clients", 0)

with col2:
    deals_file = DATA_DIR / "deal_pipeline.csv"
    if deals_file.exists():
        import pandas as pd
        try:
            df = pd.read_csv(deals_file)
            st.metric("Deals", len(df))
        except:
            st.metric("Deals", "Error")
    else:
        st.metric("Deals", 0)

with col3:
    design_dir = BASE_DIR / "design"
    if design_dir.exists():
        files = list(design_dir.glob("*"))
        st.metric("Design Files", len(files))
    else:
        st.metric("Design Files", 0)

with col4:
    sanctions_file = DATA_DIR / "sanctions_report.csv"
    if sanctions_file.exists():
        import pandas as pd
        try:
            df = pd.read_csv(sanctions_file)
            if len(df) > 0:
                st.metric("Sanctions Alerts", len(df), delta="Review needed", delta_color="inverse")
            else:
                st.metric("Sanctions", "✅ Clear")
        except:
            st.metric("Sanctions", "Check")
    else:
        st.metric("Sanctions", "Not Run")

st.caption("💡 Tip: You can run multiple apps simultaneously on different ports")
