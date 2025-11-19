"""
Security Monitor Dashboard

Real-time security monitoring dashboard integrating overarching_security.py
for PII scanning, schema validation, and data sanitization controls.
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from overarching_security import check_csv_schema, detect_pii_in_csv, find_potential_secrets

st.set_page_config(page_title="Security Monitor", page_icon="🔒", layout="wide")

# Paths
DATA_DIR = BASE_DIR / "data"
CLIENTS_CSV = DATA_DIR / "clients.csv"
DEAL_CSV = DATA_DIR / "deal_pipeline.csv"

EXPECTED_CLIENT_COLUMNS = [
    "id", "name", "email", "phone", "address", 
    "optin_email", "optin_sms", "notes"
]

EXPECTED_DEAL_COLUMNS = [
    "id", "name", "stage", "ticket_size", "local_partner",
    "country", "expected_close", "risk_score", "tags", "notes"
]

# Header
st.title("🔒 Security Monitor")
st.markdown("Real-time security scanning and data validation dashboard")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Schema Validation", "🔍 PII Scan", "🔐 Secrets Detection", "🛡️ Sanitization Tools"])

# Tab 1: Schema Validation
with tab1:
    st.header("CSV Schema Validation")
    st.markdown("Verify that critical CSV files contain expected columns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Clients CSV")
        if CLIENTS_CSV.exists():
            ok, missing = check_csv_schema(str(CLIENTS_CSV), EXPECTED_CLIENT_COLUMNS)
            if ok:
                st.success("✅ Schema valid - all expected columns present")
                df = pd.read_csv(CLIENTS_CSV, nrows=0)
                st.caption(f"**Columns:** {', '.join(df.columns)}")
            else:
                st.error(f"❌ Missing columns: {', '.join(missing)}")
        else:
            st.warning("⚠️ clients.csv not found")
    
    with col2:
        st.subheader("📊 Deal Pipeline CSV")
        if DEAL_CSV.exists():
            ok, missing = check_csv_schema(str(DEAL_CSV), EXPECTED_DEAL_COLUMNS)
            if ok:
                st.success("✅ Schema valid - all expected columns present")
                df = pd.read_csv(DEAL_CSV, nrows=0)
                st.caption(f"**Columns:** {', '.join(df.columns)}")
            else:
                st.error(f"❌ Missing columns: {', '.join(missing)}")
        else:
            st.warning("⚠️ deal_pipeline.csv not found")

# Tab 2: PII Scan
with tab2:
    st.header("PII Detection Scan")
    st.markdown("Identify potential personally identifiable information in CSV files")
    
    scan_file = st.selectbox("Select file to scan:", 
                             ["clients.csv", "deal_pipeline.csv"],
                             key="pii_scan_file")
    
    if st.button("🔍 Run PII Scan", type="primary"):
        scan_path = DATA_DIR / scan_file
        if scan_path.exists():
            with st.spinner("Scanning for PII..."):
                summary = detect_pii_in_csv(str(scan_path))
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Rows", summary["rows"])
                col2.metric("Emails Found", summary["emails_found"])
                col3.metric("Phones Found", summary["phones_found"])
                col4.metric("PII Columns", len(summary["columns_with_pii_names"]))
                
                if summary["columns_with_pii_names"]:
                    st.warning("⚠️ **Columns likely containing PII:**")
                    st.write(", ".join(summary["columns_with_pii_names"]))
                    st.info("💡 **Recommendation:** Use sanitization tools before exporting or sharing data")
                else:
                    st.success("✅ No obvious PII column names detected")
        else:
            st.error(f"❌ File not found: {scan_file}")

# Tab 3: Secrets Detection
with tab3:
    st.header("Secrets & Sensitive Data Detection")
    st.markdown("Scan workspace for potential API keys, passwords, or secrets")
    
    exclude_patterns = st.multiselect(
        "Exclude directories:",
        [".git", ".venv", "data", "design", "node_modules", "__pycache__"],
        default=[".git", ".venv", "data", "design", "__pycache__"]
    )
    
    if st.button("🔐 Scan for Secrets", type="primary"):
        with st.spinner("Scanning workspace..."):
            findings = find_potential_secrets(str(BASE_DIR), exclude_dirs=exclude_patterns)
            
            if findings:
                st.warning(f"⚠️ Found {len(findings)} potential secret occurrences")
                
                # Group by file
                by_file = {}
                for fpath, lineno, excerpt in findings:
                    if fpath not in by_file:
                        by_file[fpath] = []
                    by_file[fpath].append((lineno, excerpt))
                
                for fpath, items in list(by_file.items())[:10]:  # Show first 10 files
                    with st.expander(f"📄 {Path(fpath).relative_to(BASE_DIR)} ({len(items)} matches)"):
                        for lineno, excerpt in items[:5]:  # Show first 5 per file
                            st.code(f"Line {lineno}: {excerpt[:100]}", language="text")
                
                if len(findings) > 50:
                    st.info(f"Showing first 50 of {len(findings)} findings. Review `.security-ignore` to whitelist known false positives.")
            else:
                st.success("✅ No suspicious patterns detected")

# Tab 4: Sanitization Tools
with tab4:
    st.header("Data Sanitization Tools")
    st.markdown("Remove PII from CSV files for safe sharing")
    
    st.subheader("📋 Sanitize Clients CSV")
    
    pii_columns = st.multiselect(
        "Select columns to remove (PII):",
        ["name", "email", "phone", "address", "notes"],
        default=["name", "email", "phone", "address"]
    )
    
    if CLIENTS_CSV.exists():
        df = pd.read_csv(CLIENTS_CSV)
        st.caption(f"Original file has {len(df)} rows and {len(df.columns)} columns")
        
        if st.button("🧹 Generate Sanitized CSV", type="primary"):
            try:
                sanitized_df = df.drop(columns=pii_columns, errors='ignore')
                
                st.success(f"✅ Removed {len(pii_columns)} PII columns")
                st.dataframe(sanitized_df.head(3), use_container_width=True)
                
                csv_bytes = sanitized_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Sanitized CSV",
                    data=csv_bytes,
                    file_name=f"clients_sanitized_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                st.info(f"**Retained columns:** {', '.join(sanitized_df.columns)}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ clients.csv not found")

# Sidebar: System Status
with st.sidebar:
    st.header("🛡️ Security Status")
    
    # Quick health check
    checks = {
        "Clients CSV Schema": CLIENTS_CSV.exists() and check_csv_schema(str(CLIENTS_CSV), EXPECTED_CLIENT_COLUMNS)[0],
        "Deal CSV Schema": DEAL_CSV.exists() and check_csv_schema(str(DEAL_CSV), EXPECTED_DEAL_COLUMNS)[0],
        "Security Scanner": True,
    }
    
    for name, status in checks.items():
        if status:
            st.success(f"✅ {name}")
        else:
            st.error(f"❌ {name}")
    
    st.markdown("---")
    st.caption("Last scan: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with st.expander("ℹ️ About Security Monitor"):
        st.markdown("""
        **Purpose:** Real-time security monitoring and data validation
        
        **Features:**
        - CSV schema validation
        - PII detection (emails, phones, sensitive columns)
        - Secrets scanning (API keys, passwords)
        - Data sanitization tools
        
        **Note:** These are mechanical checks, not legal compliance guarantees. 
        Consult privacy/security professionals for regulatory requirements.
        """)
