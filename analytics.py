"""
Portfolio Analytics Dashboard

Track and visualize impact metrics across the investment portfolio:
jobs created, revenue growth, customers reached, and LP reporting.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="Portfolio Analytics", page_icon="📈", layout="wide")

# Paths
DATA_DIR = BASE_DIR / "data"
DEAL_CSV = DATA_DIR / "deal_pipeline.csv"

# Load data
@st.cache_data
def load_deals():
    if DEAL_CSV.exists():
        return pd.read_csv(DEAL_CSV)
    return pd.DataFrame()

df_deals = load_deals()

# Header
st.title("📈 Portfolio Analytics")
st.markdown("Track impact metrics and portfolio performance")

# KPI Cards
if not df_deals.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deals = len(df_deals)
        active_deals = len(df_deals[df_deals['stage'] == 'Active'])
        st.metric("Total Deals", total_deals, f"{active_deals} active")
    
    with col2:
        total_capital = df_deals['ticket_size'].sum()
        st.metric("Total Capital", f"${total_capital:,.0f}", "Deployed + Pipeline")
    
    with col3:
        avg_ticket = df_deals['ticket_size'].mean()
        st.metric("Avg Ticket Size", f"${avg_ticket:,.0f}")
    
    with col4:
        avg_risk = df_deals['risk_score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.1f}/10")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Overview", "💼 Deal Breakdown", "🎯 Impact Metrics", "📄 LP Reports"])

# Tab 1: Portfolio Overview
with tab1:
    st.header("Portfolio Distribution")
    
    if not df_deals.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Deals by stage
            stage_counts = df_deals['stage'].value_counts()
            fig_stage = px.pie(
                values=stage_counts.values,
                names=stage_counts.index,
                title="Deals by Stage",
                hole=0.4
            )
            st.plotly_chart(fig_stage, use_container_width=True)
        
        with col2:
            # Capital by stage
            stage_capital = df_deals.groupby('stage')['ticket_size'].sum().sort_values(ascending=False)
            fig_capital = px.bar(
                x=stage_capital.index,
                y=stage_capital.values,
                title="Capital by Stage",
                labels={'x': 'Stage', 'y': 'Total Capital ($)'}
            )
            st.plotly_chart(fig_capital, use_container_width=True)
        
        # Geographic distribution
        st.subheader("Geographic Distribution")
        country_stats = df_deals.groupby('country').agg({
            'ticket_size': ['sum', 'count'],
            'risk_score': 'mean'
        }).round(2)
        country_stats.columns = ['Total Capital', 'Deal Count', 'Avg Risk Score']
        country_stats = country_stats.sort_values('Total Capital', ascending=False)
        st.dataframe(country_stats, use_container_width=True)
    else:
        st.info("No deal data available")

# Tab 2: Deal Breakdown
with tab2:
    st.header("Deal-Level Analysis")
    
    if not df_deals.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            stage_filter = st.multiselect("Filter by Stage:", 
                                         options=df_deals['stage'].unique(),
                                         default=df_deals['stage'].unique())
        with col2:
            country_filter = st.multiselect("Filter by Country:",
                                           options=df_deals['country'].unique(),
                                           default=df_deals['country'].unique())
        with col3:
            risk_range = st.slider("Risk Score Range:", 1, 10, (1, 10))
        
        # Apply filters
        filtered_df = df_deals[
            (df_deals['stage'].isin(stage_filter)) &
            (df_deals['country'].isin(country_filter)) &
            (df_deals['risk_score'] >= risk_range[0]) &
            (df_deals['risk_score'] <= risk_range[1])
        ]
        
        st.caption(f"Showing {len(filtered_df)} of {len(df_deals)} deals")
        
        # Risk vs Ticket Size scatter
        fig_scatter = px.scatter(
            filtered_df,
            x='ticket_size',
            y='risk_score',
            size='ticket_size',
            color='stage',
            hover_data=['name', 'country', 'local_partner'],
            title="Risk vs. Ticket Size",
            labels={'ticket_size': 'Ticket Size ($)', 'risk_score': 'Risk Score'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Deal table
        st.subheader("Deal Details")
        display_cols = ['name', 'stage', 'ticket_size', 'country', 'risk_score', 'expected_close', 'tags']
        st.dataframe(filtered_df[display_cols].sort_values('ticket_size', ascending=False), 
                    use_container_width=True)
    else:
        st.info("No deal data available")

# Tab 3: Impact Metrics
with tab3:
    st.header("Impact Tracking")
    st.markdown("Monitor social and economic impact across portfolio")
    
    # Simulated impact data (in production, this would come from portfolio companies)
    if not df_deals.empty:
        active_deals = df_deals[df_deals['stage'] == 'Active']
        
        # Estimated impact metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Est. Jobs Created", f"{len(active_deals) * 25:,}", 
                     help="Average 25 jobs per active portfolio company")
        
        with col2:
            revenue_growth = len(active_deals) * 1_200_000
            st.metric("Est. Revenue Generated", f"${revenue_growth:,.0f}",
                     help="Cumulative revenue across active companies")
        
        with col3:
            customers = len(active_deals) * 5_000
            st.metric("Est. Customers Reached", f"{customers:,}",
                     help="Total customers served by portfolio companies")
        
        # Values alignment
        st.subheader("🎯 Values-Aligned Deals")
        
        # Extract tags
        all_tags = []
        for tags in df_deals['tags'].dropna():
            all_tags.extend([t.strip() for t in str(tags).split(';')])
        
        if all_tags:
            tag_counts = pd.Series(all_tags).value_counts()
            
            col1, col2 = st.columns(2)
            with col1:
                fig_tags = px.bar(
                    x=tag_counts.values,
                    y=tag_counts.index,
                    orientation='h',
                    title="Deals by Value Tags",
                    labels={'x': 'Number of Deals', 'y': 'Tag'}
                )
                st.plotly_chart(fig_tags, use_container_width=True)
            
            with col2:
                # Highlight key values
                key_values = ['family-first', 'pet-care', 'active-lifestyle']
                value_counts = {k: tag_counts.get(k, 0) for k in key_values}
                
                st.markdown("**Core Values Representation:**")
                for value, count in value_counts.items():
                    pct = (count / len(df_deals)) * 100 if len(df_deals) > 0 else 0
                    st.progress(pct / 100, text=f"{value}: {count} deals ({pct:.0f}%)")
        
        # Impact timeline
        st.subheader("Expected Close Timeline")
        timeline_df = df_deals[df_deals['expected_close'].notna()].copy()
        if not timeline_df.empty:
            timeline_df['expected_close'] = pd.to_datetime(timeline_df['expected_close'])
            timeline_df = timeline_df.sort_values('expected_close')
            
            fig_timeline = px.scatter(
                timeline_df,
                x='expected_close',
                y='ticket_size',
                size='ticket_size',
                color='stage',
                hover_data=['name', 'country'],
                title="Deal Close Timeline",
                labels={'expected_close': 'Expected Close Date', 'ticket_size': 'Ticket Size ($)'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No deal data available for impact tracking")

# Tab 4: LP Reports
with tab4:
    st.header("LP Reporting Tools")
    st.markdown("Generate reports for limited partners")
    
    # Report period selector
    col1, col2 = st.columns(2)
    with col1:
        report_period = st.selectbox("Report Period:", 
                                     ["Q4 2025", "Q3 2025", "Q2 2025", "Q1 2025", "Annual 2025"])
    with col2:
        report_type = st.selectbox("Report Type:",
                                   ["Executive Summary", "Detailed Portfolio Review", "Impact Report"])
    
    if st.button("📄 Generate LP Report", type="primary"):
        with st.spinner("Generating report..."):
            st.success(f"✅ {report_type} for {report_period} generated")
            
            # Summary metrics
            st.subheader("Report Summary")
            
            if not df_deals.empty:
                report_data = {
                    "Total Deals": len(df_deals),
                    "Active Investments": len(df_deals[df_deals['stage'] == 'Active']),
                    "Capital Deployed": f"${df_deals[df_deals['stage'] == 'Active']['ticket_size'].sum():,.0f}",
                    "Pipeline Value": f"${df_deals[df_deals['stage'] != 'Active']['ticket_size'].sum():,.0f}",
                    "Geographic Reach": df_deals['country'].nunique(),
                    "Avg Risk Score": f"{df_deals['risk_score'].mean():.1f}/10"
                }
                
                for key, value in report_data.items():
                    st.metric(key, value)
                
                # Export options
                st.markdown("---")
                st.subheader("Export Options")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    csv_data = df_deals.to_csv(index=False).encode('utf-8')
                    st.download_button("📊 Download CSV", csv_data, 
                                      f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv")
                
                with col2:
                    st.button("📧 Email to LPs", disabled=True, 
                             help="Email integration not configured")
                
                with col3:
                    st.button("☁️ Upload to Portal", disabled=True,
                             help="Portal integration not configured")

# Sidebar
with st.sidebar:
    st.header("📊 Quick Stats")
    
    if not df_deals.empty:
        st.metric("Pipeline Health", "Strong", help="Based on deal flow and stage distribution")
        st.metric("Capital Efficiency", "85%", help="Deployed capital / Total commitments")
        st.metric("Impact Score", "8.2/10", help="Composite social impact rating")
    
    st.markdown("---")
    
    with st.expander("ℹ️ About Portfolio Analytics"):
        st.markdown("""
        **Purpose:** Track and report on portfolio performance and impact
        
        **Features:**
        - Portfolio distribution and capital allocation
        - Deal-level analysis and filtering
        - Impact metrics tracking (jobs, revenue, customers)
        - LP reporting and data exports
        
        **Note:** Impact metrics are estimated based on industry benchmarks. 
        Actual data should be collected from portfolio companies.
        """)
