import streamlit as st
import pandas as pd
import os
import csv
import sys
from pathlib import Path

# Add tools directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "tools"))

from financial_model import npv, irr

st.set_page_config(page_title="Financial Modeling", layout="wide")

DATA_DIR = BASE_DIR / "data"
FINANCIALS_CSV = DATA_DIR / "financials_fixture.csv"

st.title("💰 Financial Modeling Dashboard")
st.markdown("**NPV & IRR Analysis for Investment Deals**")

# Sidebar: discount rate input
st.sidebar.header("Analysis Parameters")
discount_rate = st.sidebar.slider("Discount Rate (%)", min_value=1, max_value=50, value=10, step=1) / 100
st.sidebar.info(f"Using discount rate: {discount_rate*100:.2f}%")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📊 Quick Calculator", "📁 CSV Upload", "📈 Portfolio View"])

with tab1:
    st.subheader("Quick Cash Flow Calculator")
    st.markdown("Enter cash flows manually to calculate NPV and IRR.")
    
    with st.form("manual_cashflow"):
        col1, col2 = st.columns(2)
        
        with col1:
            initial_investment = st.number_input(
                "Initial Investment (negative)", 
                value=-50000, 
                step=1000,
                help="Enter as negative number (e.g., -50000)"
            )
        
        with col2:
            num_periods = st.number_input("Number of Periods", min_value=1, max_value=20, value=5)
        
        st.markdown("**Expected Returns by Period:**")
        cashflows = [initial_investment]
        
        cols = st.columns(min(num_periods, 5))
        for i in range(num_periods):
            col_idx = i % 5
            with cols[col_idx]:
                cf = st.number_input(f"Period {i+1}", value=15000 + (i * 5000), step=1000, key=f"cf_{i}")
                cashflows.append(cf)
        
        calculate = st.form_submit_button("Calculate NPV & IRR")
        
        if calculate:
            try:
                npv_result = npv(discount_rate, cashflows)
                irr_result = irr(cashflows)
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("NPV", f"${npv_result:,.2f}")
                    if npv_result > 0:
                        st.success("✅ Positive NPV - Good investment")
                    else:
                        st.warning("⚠️ Negative NPV - Review required")
                
                with col2:
                    st.metric("IRR", f"{irr_result*100:.2f}%")
                    if irr_result > discount_rate:
                        st.success(f"✅ IRR exceeds discount rate")
                    else:
                        st.warning("⚠️ IRR below discount rate")
                
                with col3:
                    total_inflow = sum([c for c in cashflows if c > 0])
                    roi = ((total_inflow + initial_investment) / abs(initial_investment)) * 100
                    st.metric("Simple ROI", f"{roi:.1f}%")
                
                # Cash flow table
                st.markdown("**Cash Flow Summary:**")
                df = pd.DataFrame({
                    'Period': range(len(cashflows)),
                    'Cash Flow': cashflows,
                    'Discounted Value': [cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cashflows)]
                })
                st.dataframe(df.style.format({
                    'Cash Flow': '${:,.2f}',
                    'Discounted Value': '${:,.2f}'
                }), use_container_width=True)
                
            except Exception as e:
                st.error(f"Calculation error: {e}")

with tab2:
    st.subheader("Upload CSV for Analysis")
    st.markdown("CSV format: `period,cashflow` (negative for investments, positive for returns)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df, use_container_width=True)
                
                if 'cashflow' in df.columns:
                    cashflows = df['cashflow'].tolist()
                    
                    npv_result = npv(discount_rate, cashflows)
                    irr_result = irr(cashflows)
                    
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("NPV", f"${npv_result:,.2f}")
                    
                    with col2:
                        st.metric("IRR", f"{irr_result*100:.2f}%")
                    
                    with col3:
                        total = sum(cashflows)
                        st.metric("Total Net Cash", f"${total:,.2f}")
                    
                    # Add discounted values
                    df['Discounted Value'] = [cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cashflows)]
                    
                    st.markdown("**Analysis with Discounted Values:**")
                    st.dataframe(df.style.format({
                        'cashflow': '${:,.2f}',
                        'Discounted Value': '${:,.2f}'
                    }), use_container_width=True)
                else:
                    st.error("CSV must contain a 'cashflow' column")
                    
            except Exception as e:
                st.error(f"Error processing CSV: {e}")
    
    with col2:
        st.markdown("**Load Example:**")
        if st.button("Load Fixture Data"):
            if FINANCIALS_CSV.exists():
                try:
                    df = pd.read_csv(FINANCIALS_CSV)
                    cashflows = df['cashflow'].tolist()
                    
                    npv_result = npv(discount_rate, cashflows)
                    irr_result = irr(cashflows)
                    
                    st.success("Loaded fixture data")
                    st.dataframe(df)
                    st.metric("NPV", f"${npv_result:,.2f}")
                    st.metric("IRR", f"{irr_result*100:.2f}%")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("No fixture file found")

with tab3:
    st.subheader("Multi-Deal Portfolio Comparison")
    st.markdown("Compare multiple investment scenarios side-by-side.")
    
    # Example portfolio deals
    deals = {
        "Deal A - Family Housing": [-100000, 30000, 35000, 40000, 45000, 50000],
        "Deal B - Pet Services": [-75000, 20000, 25000, 30000, 35000, 40000],
        "Deal C - Active Lifestyle": [-150000, 40000, 50000, 60000, 70000, 80000]
    }
    
    results = []
    for deal_name, cashflows in deals.items():
        try:
            npv_val = npv(discount_rate, cashflows)
            irr_val = irr(cashflows)
            total_inflow = sum([c for c in cashflows if c > 0])
            investment = abs(cashflows[0])
            
            results.append({
                'Deal': deal_name,
                'Investment': investment,
                'Total Returns': total_inflow,
                'NPV': npv_val,
                'IRR (%)': irr_val * 100,
                'ROI (%)': ((total_inflow - investment) / investment) * 100
            })
        except Exception as e:
            st.warning(f"Could not calculate {deal_name}: {e}")
    
    if results:
        portfolio_df = pd.DataFrame(results)
        
        st.dataframe(portfolio_df.style.format({
            'Investment': '${:,.0f}',
            'Total Returns': '${:,.0f}',
            'NPV': '${:,.2f}',
            'IRR (%)': '{:.2f}%',
            'ROI (%)': '{:.1f}%'
        }).background_gradient(subset=['NPV', 'IRR (%)'], cmap='RdYlGn'), 
        use_container_width=True)
        
        # Summary metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_investment = portfolio_df['Investment'].sum()
            st.metric("Total Portfolio Investment", f"${total_investment:,.0f}")
        
        with col2:
            total_npv = portfolio_df['NPV'].sum()
            st.metric("Portfolio NPV", f"${total_npv:,.0f}")
        
        with col3:
            avg_irr = portfolio_df['IRR (%)'].mean()
            st.metric("Average IRR", f"{avg_irr:.2f}%")
        
        with col4:
            portfolio_roi = ((portfolio_df['Total Returns'].sum() - total_investment) / total_investment) * 100
            st.metric("Portfolio ROI", f"{portfolio_roi:.1f}%")
        
        # Download results
        csv_bytes = portfolio_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Portfolio Analysis",
            data=csv_bytes,
            file_name=f"portfolio_analysis_{discount_rate*100:.0f}pct.csv",
            mime='text/csv'
        )

# Footer
st.markdown("---")
st.caption("📊 Financial calculations use discounted cash flow (DCF) methodology. IRR computed via Newton-Raphson method.")
