import streamlit as st
import pandas as pd
import os
import csv
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add scripts directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

try:
    import requests
except ImportError:
    requests = None

st.set_page_config(page_title="Compliance & Sanctions", layout="wide")

DATA_DIR = BASE_DIR / "data"
DEALS_CSV = DATA_DIR / "deal_pipeline.csv"
CLIENTS_CSV = DATA_DIR / "clients.csv"
REPORT_CSV = DATA_DIR / "sanctions_report.csv"
AUDIT_LOG = DATA_DIR / "compliance_audit.csv"

OFAC_SDN_CSV = 'https://home.treasury.gov/system/files/126/SDN.csv'

st.title("🛡️ Compliance & Sanctions Screening")
st.markdown("**OFAC SDN List Screening for Clients and Deals**")

# Helper functions
def normalize(name: str) -> str:
    """Normalize name for matching."""
    if not name:
        return ''
    s = name.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_targets() -> List[Dict]:
    """Load all names from deals and clients."""
    targets = []
    
    # Load from deals
    if DEALS_CSV.exists():
        try:
            df = pd.read_csv(DEALS_CSV, dtype=str, keep_default_na=False)
            for _, row in df.iterrows():
                deal_id = row.get('id', row.get('deal_id', ''))
                name = row.get('name', row.get('deal_name', ''))
                if name:
                    targets.append({
                        'source': 'deal_pipeline',
                        'id': deal_id,
                        'name': name,
                        'type': 'Company/Deal',
                        'status': row.get('sanctions_status', 'Pending')
                    })
                
                # Also check local partner
                partner = row.get('local_partner', '')
                if partner:
                    targets.append({
                        'source': 'deal_pipeline',
                        'id': deal_id,
                        'name': partner,
                        'type': 'Partner',
                        'status': row.get('sanctions_status', 'Pending')
                    })
        except Exception as e:
            st.warning(f"Could not load deals: {e}")
    
    # Load from clients
    if CLIENTS_CSV.exists():
        try:
            df = pd.read_csv(CLIENTS_CSV, dtype=str, keep_default_na=False)
            for _, row in df.iterrows():
                name = row.get('name', '')
                if name:
                    targets.append({
                        'source': 'clients',
                        'id': row.get('id', ''),
                        'name': name,
                        'type': 'Client',
                        'status': 'Pending'
                    })
        except Exception as e:
            st.warning(f"Could not load clients: {e}")
    
    return targets

def fetch_ofac_names() -> List[str]:
    """Fetch OFAC SDN list."""
    if requests is None:
        st.error("requests library required. Run: pip install requests")
        return []
    
    try:
        with st.spinner("Fetching OFAC SDN list..."):
            resp = requests.get(OFAC_SDN_CSV, timeout=30)
            if resp.status_code != 200:
                st.error(f"OFAC fetch failed: HTTP {resp.status_code}")
                return []
            
            text = resp.text.splitlines()
            reader = csv.reader(text)
            headers = next(reader, None)
            
            # Find name column
            name_idx = 0
            if headers:
                for i, h in enumerate(headers):
                    if h and 'name' in h.lower():
                        name_idx = i
                        break
            
            names = []
            for row in reader:
                if row and name_idx < len(row):
                    names.append(row[name_idx])
            
            return names
    except Exception as e:
        st.error(f"Error fetching OFAC: {e}")
        return []

def match_targets(targets: List[Dict], sanc_names: List[str]) -> List[Dict]:
    """Match targets against sanctions list."""
    sanc_norm = [(normalize(s), s) for s in sanc_names if s]
    findings = []
    
    for target in targets:
        tn = normalize(target['name'])
        if not tn:
            continue
        
        for sn, raw in sanc_norm:
            if not sn:
                continue
            
            # Substring match (conservative)
            if tn in sn or sn in tn:
                findings.append({
                    'target_name': target['name'],
                    'target_type': target['type'],
                    'target_id': target['id'],
                    'source': target['source'],
                    'sanctioned_name': raw,
                    'checked_at': datetime.utcnow().isoformat(),
                    'match_confidence': 'Medium'  # Could be enhanced
                })
                break
    
    return findings

def log_audit_entry(action: str, details: str):
    """Log compliance actions."""
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'details': details,
        'user': os.getenv('USER', 'system')
    }
    
    # Append to audit log
    file_exists = AUDIT_LOG.exists()
    with open(AUDIT_LOG, 'a', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['timestamp', 'action', 'details', 'user'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

# Sidebar
st.sidebar.header("Screening Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh OFAC data", value=False)
show_cleared = st.sidebar.checkbox("Show cleared items", value=False)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Screening Queue", "📋 Results", "✅ Clearance", "📊 Audit Log"])

with tab1:
    st.subheader("Names to Screen")
    
    targets = load_targets()
    
    if not targets:
        st.info("No targets found. Add clients or deals first.")
    else:
        st.write(f"**{len(targets)} names loaded from clients and deals**")
        
        # Show targets table
        targets_df = pd.DataFrame(targets)
        st.dataframe(targets_df, use_container_width=True)
        
        st.markdown("---")
        
        if st.button("🔍 Run OFAC Screening", type="primary"):
            sanc_names = fetch_ofac_names()
            
            if sanc_names:
                st.success(f"Loaded {len(sanc_names)} names from OFAC SDN")
                
                findings = match_targets(targets, sanc_names)
                
                if findings:
                    st.error(f"⚠️ Found {len(findings)} potential matches")
                    
                    # Save report
                    findings_df = pd.DataFrame(findings)
                    findings_df.to_csv(REPORT_CSV, index=False)
                    
                    st.dataframe(findings_df, use_container_width=True)
                    
                    # Log action
                    log_audit_entry(
                        "sanctions_check",
                        f"Screened {len(targets)} names, found {len(findings)} matches"
                    )
                    
                    # Download findings
                    csv_bytes = findings_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Findings Report",
                        data=csv_bytes,
                        file_name=f"sanctions_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
                else:
                    st.success("✅ No sanctions matches found")
                    
                    # Clear any existing report
                    if REPORT_CSV.exists():
                        REPORT_CSV.unlink()
                    
                    log_audit_entry(
                        "sanctions_check",
                        f"Screened {len(targets)} names, no matches"
                    )

with tab2:
    st.subheader("Screening Results")
    
    if REPORT_CSV.exists():
        try:
            findings_df = pd.read_csv(REPORT_CSV)
            
            if findings_df.empty:
                st.info("No findings in report")
            else:
                st.warning(f"**{len(findings_df)} active findings**")
                
                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    filter_type = st.multiselect(
                        "Filter by Type",
                        options=findings_df['target_type'].unique().tolist() if 'target_type' in findings_df.columns else [],
                        default=findings_df['target_type'].unique().tolist() if 'target_type' in findings_df.columns else []
                    )
                
                with col2:
                    filter_source = st.multiselect(
                        "Filter by Source",
                        options=findings_df['source'].unique().tolist() if 'source' in findings_df.columns else [],
                        default=findings_df['source'].unique().tolist() if 'source' in findings_df.columns else []
                    )
                
                # Apply filters
                filtered_df = findings_df.copy()
                if filter_type and 'target_type' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['target_type'].isin(filter_type)]
                if filter_source and 'source' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['source'].isin(filter_source)]
                
                st.dataframe(filtered_df, use_container_width=True)
                
                # Download filtered results
                csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Filtered Results",
                    data=csv_bytes,
                    file_name=f"sanctions_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )
                
        except Exception as e:
            st.error(f"Error loading report: {e}")
    else:
        st.info("No sanctions report found. Run screening first.")

with tab3:
    st.subheader("Manual Clearance Workflow")
    st.markdown("Review and clear false positives or approve confirmed matches.")
    
    if REPORT_CSV.exists():
        try:
            findings_df = pd.read_csv(REPORT_CSV)
            
            if not findings_df.empty:
                for idx, row in findings_df.iterrows():
                    with st.expander(f"🔍 {row.get('target_name', 'Unknown')} → {row.get('sanctioned_name', 'Unknown')}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Target:** {row.get('target_name', 'N/A')}")
                            st.write(f"**Type:** {row.get('target_type', 'N/A')}")
                            st.write(f"**Source:** {row.get('source', 'N/A')}")
                            st.write(f"**Sanctioned Name:** {row.get('sanctioned_name', 'N/A')}")
                            st.write(f"**Checked:** {row.get('checked_at', 'N/A')}")
                        
                        with col2:
                            decision = st.radio(
                                "Decision",
                                ["Pending", "Clear - False Positive", "Escalate"],
                                key=f"decision_{idx}"
                            )
                            
                            if st.button("Apply", key=f"apply_{idx}"):
                                log_audit_entry(
                                    "manual_review",
                                    f"{decision} - {row.get('target_name')} vs {row.get('sanctioned_name')}"
                                )
                                
                                if decision == "Clear - False Positive":
                                    # Remove from findings
                                    findings_df = findings_df.drop(idx)
                                    findings_df.to_csv(REPORT_CSV, index=False)
                                    st.success("Cleared and removed from findings")
                                    st.rerun()
                                else:
                                    st.info(f"Status: {decision}")
            else:
                st.success("✅ No pending findings to review")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("No findings to review")

with tab4:
    st.subheader("Compliance Audit Log")
    
    if AUDIT_LOG.exists():
        try:
            audit_df = pd.read_csv(AUDIT_LOG)
            
            # Show summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Actions", len(audit_df))
            with col2:
                recent = audit_df[audit_df['timestamp'] >= (datetime.utcnow().isoformat()[:10])]
                st.metric("Actions Today", len(recent))
            with col3:
                if 'action' in audit_df.columns:
                    checks = len(audit_df[audit_df['action'] == 'sanctions_check'])
                    st.metric("Total Screenings", checks)
            
            # Show recent entries
            st.markdown("**Recent Activity:**")
            recent_df = audit_df.tail(50).iloc[::-1]  # Last 50, reversed
            st.dataframe(recent_df, use_container_width=True)
            
            # Download full log
            csv_bytes = audit_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Full Audit Log",
                data=csv_bytes,
                file_name=f"compliance_audit_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
            
        except Exception as e:
            st.error(f"Error loading audit log: {e}")
    else:
        st.info("No audit entries yet")

# Footer
st.markdown("---")
st.caption("🛡️ Sanctions screening uses OFAC SDN list. Results require manual review for false positives.")
st.caption("⚠️ This tool is for preliminary screening only. Consult legal counsel for compliance decisions.")
