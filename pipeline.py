import streamlit as st
import pandas as pd
import os
import uuid
import csv

st.set_page_config(page_title="Deal Pipeline", layout="wide")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DEALS_CSV = os.path.join(DATA_DIR, 'deal_pipeline.csv')

CSV_COLUMNS = [
    'id','name','stage','ticket_size','local_partner','country','expected_close','risk_score','tags','notes'
]

def read_deals():
    if not os.path.exists(DEALS_CSV):
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(DEALS_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
        return df
    try:
        return pd.read_csv(DEALS_CSV, dtype=str, keep_default_na=False)
    except Exception:
        return pd.DataFrame(columns=CSV_COLUMNS)

def write_deals(df: pd.DataFrame):
    df.to_csv(DEALS_CSV, index=False, quoting=csv.QUOTE_MINIMAL)


st.title('Deal Pipeline')

df = read_deals()

with st.expander('Add new deal'):
    with st.form('add_deal'):
        name = st.text_input('Company name')
        stage = st.selectbox('Stage', ['New','Sourced','Screening','Term Sheet','Due Diligence','Closed-Won','Closed-Lost'])
        ticket_size = st.number_input('Ticket size (USD)', min_value=0, value=50000, step=1000)
        local_partner = st.text_input('Local partner')
        country = st.text_input('Country')
        expected_close = st.date_input('Expected close date')
        risk_score = st.slider('Risk score (1 low - 10 high)', 1, 10, 5)
        tags = st.text_input('Tags (comma separated) — try: family-first, pet-care, active-lifestyle')
        notes = st.text_area('Notes')
        submitted = st.form_submit_button('Add deal')
        if submitted:
            new = {
                'id': uuid.uuid4().hex,
                'name': name,
                'stage': stage,
                'ticket_size': str(ticket_size),
                'local_partner': local_partner,
                'country': country,
                'expected_close': expected_close.isoformat(),
                'risk_score': str(risk_score),
                'tags': ",".join([t.strip() for t in tags.split(",") if t.strip()]),
                'notes': notes,
            }
            df = df.append(new, ignore_index=True)
            write_deals(df)
            st.success('Deal added')

st.subheader('Pipeline table')
st.dataframe(df)

csv_bytes = df.to_csv(index=False).encode('utf-8')
st.download_button('Download pipeline CSV', data=csv_bytes, file_name='deal_pipeline.csv')

with st.expander('Edit existing deal'):
    ids = list(df['id'])
    if ids:
        sel = st.selectbox('Select deal to edit', ids)
        row = df[df['id'] == sel].iloc[0]
        with st.form('edit_deal'):
            name_e = st.text_input('Company name', value=row.get('name',''))
            stage_e = st.selectbox('Stage', ['New','Sourced','Screening','Term Sheet','Due Diligence','Closed-Won','Closed-Lost'], index=['New','Sourced','Screening','Term Sheet','Due Diligence','Closed-Won','Closed-Lost'].index(row.get('stage','New')) if row.get('stage') in ['New','Sourced','Screening','Term Sheet','Due Diligence','Closed-Won','Closed-Lost'] else 0)
            ticket_size_e = st.number_input('Ticket size (USD)', min_value=0, value=int(float(row.get('ticket_size',0))), step=1000)
            local_partner_e = st.text_input('Local partner', value=row.get('local_partner',''))
            country_e = st.text_input('Country', value=row.get('country',''))
            # expected_close as text for simplicity
            expected_close_e = st.text_input('Expected close (YYYY-MM-DD)', value=row.get('expected_close',''))
            risk_score_e = st.slider('Risk score (1 low - 10 high)', 1, 10, int(float(row.get('risk_score',5))))
            tags_e = st.text_input('Tags (comma separated)', value=row.get('tags',''))
            notes_e = st.text_area('Notes', value=row.get('notes',''))
            updated = st.form_submit_button('Save changes')
            if updated:
                df.loc[df['id'] == sel, 'name'] = name_e
                df.loc[df['id'] == sel, 'stage'] = stage_e
                df.loc[df['id'] == sel, 'ticket_size'] = str(ticket_size_e)
                df.loc[df['id'] == sel, 'local_partner'] = local_partner_e
                df.loc[df['id'] == sel, 'country'] = country_e
                df.loc[df['id'] == sel, 'expected_close'] = expected_close_e
                df.loc[df['id'] == sel, 'risk_score'] = str(risk_score_e)
                df.loc[df['id'] == sel, 'tags'] = ",".join([t.strip() for t in tags_e.split(",") if t.strip()])
                df.loc[df['id'] == sel, 'notes'] = notes_e
                write_deals(df)
                st.success('Deal updated')
    else:
        st.info('No deals to edit')
