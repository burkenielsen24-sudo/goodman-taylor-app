import streamlit as st
import pandas as pd
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    requests = None

st.set_page_config(page_title="Data Enrichment", layout="wide")

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DEALS_CSV = DATA_DIR / "deal_pipeline.csv"
ENRICHED_CSV = DATA_DIR / "deal_pipeline_enriched.csv"

OC_BASE = 'https://api.opencorporates.com/v0.4'

COUNTRY_TO_CURRENCY = {
    'Kenya': 'KES', 'Liberia': 'LRD', 'Nigeria': 'NGN', 'Ghana': 'GHS',
    'India': 'INR', 'United States': 'USD', 'UK': 'GBP', 'Uganda': 'UGX',
    'Tanzania': 'TZS', 'Rwanda': 'RWF', 'South Africa': 'ZAR'
}

st.title("🔍 Data Enrichment Dashboard")
st.markdown("**Enrich deals with OpenCorporates and currency data**")

# Sidebar config
st.sidebar.header("API Configuration")
oc_api_key = st.sidebar.text_input(
    "OpenCorporates API Key (optional)",
    type="password",
    help="Increases rate limits. Get one at opencorporates.com"
)

if not oc_api_key:
    oc_api_key = os.getenv('OPEN_CORPORATES_API_KEY')

use_cached = st.sidebar.checkbox("Use cached enriched data if available", value=True)
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Free API limits: ~500 requests/month")

# Helper functions
@st.cache_data(ttl=3600)
def search_opencorporates(name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Search OpenCorporates for company info."""
    if requests is None:
        return {'error': 'requests library required'}
    
    try:
        params = {'q': name}
        if api_key:
            params['api_token'] = api_key
        
        url = f"{OC_BASE}/companies/search"
        resp = requests.get(url, params=params, timeout=15)
        
        if resp.status_code != 200:
            return {'error': f'HTTP {resp.status_code}'}
        
        data = resp.json()
        if 'results' in data and data['results'].get('companies'):
            companies = data['results']['companies']
            if companies:
                comp = companies[0]['company']
                return {
                    'company_number': comp.get('company_number', ''),
                    'jurisdiction_code': comp.get('jurisdiction_code', ''),
                    'incorporation_date': comp.get('incorporation_date', ''),
                    'company_type': comp.get('company_type', ''),
                    'registry_url': comp.get('opencorporates_url', ''),
                    'current_status': comp.get('current_status', ''),
                    'registered_address': comp.get('registered_address_in_full', ''),
                    'officers_count': len(comp.get('officers', [])) if 'officers' in comp else 0
                }
        return {'info': 'No results found'}
    except Exception as e:
        return {'error': str(e)}

@st.cache_data(ttl=86400)
def get_fx_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate."""
    if requests is None:
        return 1.0
    
    if from_currency == to_currency:
        return 1.0
    
    try:
        url = 'https://api.exchangerate.host/latest'
        params = {'base': from_currency, 'symbols': to_currency}
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.status_code != 200:
            return 1.0
        
        data = resp.json()
        rate = data.get('rates', {}).get(to_currency)
        return float(rate) if rate else 1.0
    except Exception:
        return 1.0

def calculate_data_quality_score(row: Dict) -> int:
    """Calculate data quality score 0-100."""
    score = 0
    
    # Basic fields (40 points)
    if row.get('name'): score += 10
    if row.get('country'): score += 10
    if row.get('ticket_size') and str(row['ticket_size']) != '0': score += 10
    if row.get('stage'): score += 10
    
    # Enrichment data (60 points)
    if row.get('company_number'): score += 20
    if row.get('jurisdiction_code'): score += 10
    if row.get('incorporation_date'): score += 15
    if row.get('registry_url'): score += 10
    if row.get('fx_rate') and row.get('fx_rate') != 1.0: score += 5
    
    return min(score, 100)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Pipeline Status", "🔄 Enrich Deals", "📊 Data Quality", "🌍 Currency Tools"])

with tab1:
    st.subheader("Current Deal Pipeline")
    
    if not DEALS_CSV.exists():
        st.warning("No deal pipeline found. Add deals first.")
    else:
        df = pd.read_csv(DEALS_CSV, dtype=str, keep_default_na=False)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Deals", len(df))
        with col2:
            enriched_exists = ENRICHED_CSV.exists()
            st.metric("Enriched", "Yes" if enriched_exists else "No")
        with col3:
            countries = df['country'].nunique() if 'country' in df.columns else 0
            st.metric("Countries", countries)
        with col4:
            total_value = df['ticket_size'].astype(float).sum() if 'ticket_size' in df.columns else 0
            st.metric("Total Value", f"${total_value:,.0f}")
        
        st.markdown("---")
        
        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            if 'stage' in df.columns:
                stage_filter = st.multiselect(
                    "Filter by Stage",
                    options=df['stage'].unique().tolist(),
                    default=df['stage'].unique().tolist()
                )
                if stage_filter:
                    df = df[df['stage'].isin(stage_filter)]
        
        with col2:
            if 'country' in df.columns:
                country_filter = st.multiselect(
                    "Filter by Country",
                    options=df['country'].unique().tolist(),
                    default=df['country'].unique().tolist()
                )
                if country_filter:
                    df = df[df['country'].isin(country_filter)]
        
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Enrich Deal Data")
    st.markdown("Fetch company information from OpenCorporates and currency rates.")
    
    if not DEALS_CSV.exists():
        st.warning("No deals to enrich")
    else:
        df = pd.read_csv(DEALS_CSV, dtype=str, keep_default_na=False)
        
        # Show enrichment options
        col1, col2 = st.columns(2)
        
        with col1:
            enrich_mode = st.radio(
                "Enrichment Mode",
                ["Single Deal", "Batch (All Deals)", "Batch (Selected)"]
            )
        
        with col2:
            data_sources = st.multiselect(
                "Data Sources",
                ["OpenCorporates", "Currency Rates"],
                default=["OpenCorporates", "Currency Rates"]
            )
        
        if enrich_mode == "Single Deal":
            deal_names = df['name'].tolist() if 'name' in df.columns else []
            if deal_names:
                selected_deal = st.selectbox("Select Deal", deal_names)
                
                if st.button("🔍 Enrich Selected Deal", type="primary"):
                    deal_row = df[df['name'] == selected_deal].iloc[0]
                    
                    with st.spinner(f"Enriching {selected_deal}..."):
                        result = {}
                        
                        # OpenCorporates enrichment
                        if "OpenCorporates" in data_sources:
                            oc_data = search_opencorporates(selected_deal, oc_api_key)
                            result.update(oc_data)
                        
                        # Currency enrichment
                        if "Currency Rates" in data_sources:
                            country = deal_row.get('country', '')
                            currency = COUNTRY_TO_CURRENCY.get(country, 'USD')
                            rate = get_fx_rate('USD', currency)
                            result['currency'] = currency
                            result['fx_rate_usd'] = rate
                            
                            try:
                                ticket_usd = float(deal_row.get('ticket_size', 0))
                                result['ticket_local'] = round(ticket_usd * rate, 2)
                            except:
                                result['ticket_local'] = 0
                    
                    # Display results
                    st.success("Enrichment complete!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Company Information:**")
                        if result.get('company_number'):
                            st.write(f"Company Number: `{result['company_number']}`")
                        if result.get('jurisdiction_code'):
                            st.write(f"Jurisdiction: `{result['jurisdiction_code']}`")
                        if result.get('incorporation_date'):
                            st.write(f"Incorporated: `{result['incorporation_date']}`")
                        if result.get('current_status'):
                            st.write(f"Status: `{result['current_status']}`")
                        if result.get('registry_url'):
                            st.markdown(f"[View in Registry]({result['registry_url']})")
                    
                    with col2:
                        st.markdown("**Financial Data:**")
                        if result.get('currency'):
                            st.write(f"Local Currency: `{result['currency']}`")
                        if result.get('fx_rate_usd'):
                            st.write(f"FX Rate (USD→{result.get('currency', 'local')}): `{result['fx_rate_usd']:.4f}`")
                        if result.get('ticket_local'):
                            st.write(f"Ticket (Local): `{result['ticket_local']:,.2f} {result.get('currency', '')}`")
                    
                    # Show raw data
                    with st.expander("📋 Raw JSON Response"):
                        st.json(result)
        
        elif enrich_mode == "Batch (All Deals)":
            st.warning(f"⚠️ This will enrich {len(df)} deals. API rate limits may apply.")
            
            if st.button("🚀 Start Batch Enrichment", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                enriched_rows = []
                
                for idx, row in df.iterrows():
                    status_text.text(f"Enriching {idx+1}/{len(df)}: {row.get('name', 'Unknown')}")
                    
                    enriched = row.to_dict()
                    
                    # OpenCorporates
                    if "OpenCorporates" in data_sources:
                        try:
                            oc_data = search_opencorporates(row.get('name', ''), oc_api_key)
                            enriched.update(oc_data)
                            time.sleep(1.2)  # Rate limiting
                        except:
                            pass
                    
                    # Currency
                    if "Currency Rates" in data_sources:
                        try:
                            country = row.get('country', '')
                            currency = COUNTRY_TO_CURRENCY.get(country, 'USD')
                            rate = get_fx_rate('USD', currency)
                            enriched['currency'] = currency
                            enriched['fx_rate_usd'] = rate
                            ticket_usd = float(row.get('ticket_size', 0))
                            enriched['ticket_local'] = round(ticket_usd * rate, 2)
                        except:
                            pass
                    
                    enriched_rows.append(enriched)
                    progress_bar.progress((idx + 1) / len(df))
                
                # Save enriched data
                enriched_df = pd.DataFrame(enriched_rows)
                enriched_df.to_csv(ENRICHED_CSV, index=False)
                
                status_text.text("✅ Batch enrichment complete!")
                st.success(f"Enriched {len(enriched_rows)} deals. Saved to: {ENRICHED_CSV}")
                
                st.dataframe(enriched_df, use_container_width=True)

with tab3:
    st.subheader("Data Quality Assessment")
    
    if ENRICHED_CSV.exists() and use_cached:
        df = pd.read_csv(ENRICHED_CSV, dtype=str, keep_default_na=False)
        st.info("Using enriched data")
    elif DEALS_CSV.exists():
        df = pd.read_csv(DEALS_CSV, dtype=str, keep_default_na=False)
        st.warning("Using base pipeline (not enriched)")
    else:
        st.error("No data available")
        df = None
    
    if df is not None:
        # Calculate quality scores
        df['quality_score'] = df.apply(lambda row: calculate_data_quality_score(row.to_dict()), axis=1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = df['quality_score'].mean()
            st.metric("Average Quality Score", f"{avg_score:.0f}/100")
        with col2:
            high_quality = len(df[df['quality_score'] >= 70])
            st.metric("High Quality Deals", f"{high_quality}/{len(df)}")
        with col3:
            needs_enrichment = len(df[df['quality_score'] < 50])
            st.metric("Needs Enrichment", needs_enrichment)
        
        # Quality distribution
        st.markdown("**Quality Score Distribution:**")
        quality_bins = pd.cut(df['quality_score'], bins=[0, 40, 70, 100], labels=['Low', 'Medium', 'High'])
        quality_counts = quality_bins.value_counts().sort_index()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Low (0-40)", quality_counts.get('Low', 0))
        with col2:
            st.metric("Medium (40-70)", quality_counts.get('Medium', 0))
        with col3:
            st.metric("High (70-100)", quality_counts.get('High', 0))
        
        # Detailed table
        st.markdown("---")
        display_df = df[['name', 'country', 'quality_score']].copy() if 'name' in df.columns else df
        st.dataframe(
            display_df.sort_values('quality_score', ascending=False),
            use_container_width=True
        )

with tab4:
    st.subheader("Currency Conversion Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Quick Converter:**")
        amount = st.number_input("Amount (USD)", value=50000, step=1000)
        target_currency = st.selectbox(
            "Target Currency",
            list(COUNTRY_TO_CURRENCY.values())
        )
        
        if st.button("Convert"):
            rate = get_fx_rate('USD', target_currency)
            converted = amount * rate
            st.success(f"${amount:,.2f} USD = {converted:,.2f} {target_currency}")
            st.info(f"Exchange Rate: 1 USD = {rate:.4f} {target_currency}")
    
    with col2:
        st.markdown("**Supported Countries:**")
        countries_df = pd.DataFrame(
            list(COUNTRY_TO_CURRENCY.items()),
            columns=['Country', 'Currency']
        )
        st.dataframe(countries_df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("🔍 Data enrichment powered by OpenCorporates API and exchangerate.host")
st.caption("⚠️ Free tier limits apply. For production use, consider API keys.")
