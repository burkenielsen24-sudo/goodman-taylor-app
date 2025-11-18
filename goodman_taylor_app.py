import streamlit as st
import pandas as pd
from PIL import Image
import os
import re
import uuid
import subprocess
import io
from tools.sanitize_clients import sanitize_clients

st.set_page_config(page_title="Goodman-Taylor Studio", layout="wide")

# Base folders
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DESIGN_DIR = os.path.join(BASE_DIR, 'design')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DESIGN_DIR, exist_ok=True)

CLIENTS_CSV = os.path.join(DATA_DIR, 'clients.csv')
HOME_VALUE_CSV = os.path.join(DATA_DIR, 'home_value.csv')

# CSV schema without dates
CSV_COLUMNS = [
    "id", "name", "email", "phone", "preferred_contact",
    "timeline", "address", "source", "tags", "optin_email",
    "optin_sms", "status", "notes"
]

def _is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email)) if email else True

def _normalize_phone(phone):
    return re.sub(r"[^\d+]", "", phone) if phone else ""

import csv

def save_client_record(record):
    df = pd.DataFrame([record], columns=CSV_COLUMNS)
    write_header = not os.path.exists(CLIENTS_CSV)
    df.to_csv(CLIENTS_CSV, mode='a', header=write_header, index=False, quoting=csv.QUOTE_MINIMAL)

# ... inside your intake form, after save_client_record(record) succeeds:
try:
    st.experimental_rerun()
except Exception:
    st.info("Lead saved. Refresh the page to see the new lead.")

# Intake form
st.header("📝 New Client Intake")

with st.form("intake_form", clear_on_submit=True):
    name = st.text_input("Full name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    preferred_contact = st.selectbox("Preferred contact method", ["Phone", "Email", "Text"])
    timeline = st.selectbox("Timeline to move or list", ["0-3 months", "3-6 months", "6-12 months", "12+ months", "Just browsing"])
    address = st.text_input("Property address (optional)")
    source = st.selectbox("How did they hear about you", ["Website", "YouTube", "Referral", "Social", "Other"])
    tags = st.text_input("Tags (comma separated) — e.g., WarmLead, NeedsStaging")
    optin_email = st.checkbox("Opted in to email")
    optin_sms = st.checkbox("Opted in to SMS/text")
    notes = st.text_area("Notes (private)")
    submitted = st.form_submit_button("Save lead")

    if submitted:
        if not name.strip():
            st.error("Please enter the client's name.")
        elif email and not _is_valid_email(email.strip()):
            st.error("Please enter a valid email address or leave it blank.")
        else:
            record = {
                "id": uuid.uuid4().hex,
                "name": name.strip(),
                "email": email.strip(),
                "phone": _normalize_phone(phone),
                "preferred_contact": preferred_contact,
                "timeline": timeline,
                "address": address.strip(),
                "source": source,
                "tags": ",".join([t.strip() for t in tags.split(",") if t.strip()]),
                "optin_email": bool(optin_email),
                "optin_sms": bool(optin_sms),
                "status": "New",
                "notes": notes.strip()
            }
            try:
                save_client_record(record)
                st.success("Lead saved locally to data/clients.csv")
                # after saving the record
                try:
                    st.experimental_rerun()
                except AttributeError:
                    st.info("Lead saved. Please refresh the page to see the new lead.")
            except Exception as e:
                st.error(f"Could not save lead: {e}")

# Main UI
st.title("🏡 Goodman-Taylor Studio")
st.subheader("📊 Real Estate + Interior Design Dashboard")
st.markdown("**Our mission:** We love pets, support families, and champion active living — design and real-estate solutions built for everyday life.")

# Sidebar values + upload
st.sidebar.markdown("**Our Values:** Family-first · Pet-friendly · Active-lifestyle")
st.sidebar.markdown("_I like my dog, I like helping families, and I like being active._")
st.sidebar.header("Upload Client Photo or Sketch")

# Demo mode: load demo deal fixture for showcase
demo_mode = st.sidebar.checkbox("Demo mode: show example deals")
DEAL_FIXTURE = os.path.join(DATA_DIR, 'deal_pipeline_fixture.csv')
demo_deals_df = None
if demo_mode:
    if os.path.exists(DEAL_FIXTURE):
        try:
            demo_deals_df = pd.read_csv(DEAL_FIXTURE)
        except Exception as e:
            st.sidebar.error(f"Could not load demo fixture: {e}")
    else:
        st.sidebar.info("No demo fixture found at data/deal_pipeline_fixture.csv")
uploaded_file = st.sidebar.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Design", use_column_width=True)
        safe_name = f"{uuid.uuid4().hex}_{os.path.basename(uploaded_file.name)}"
        save_path = os.path.join(DESIGN_DIR, safe_name)
        image.save(save_path)
        st.success("Image saved to design folder")
    except Exception as e:
        st.error(f"Could not process uploaded image: {e}")

# Admin panel
st.sidebar.markdown("---")
st.sidebar.header("Admin")
admin_pass = os.getenv("ADMIN_PASS")
admin_ok = True
if admin_pass:
    entered = st.sidebar.text_input("Admin passphrase", type="password")
    admin_ok = (entered == admin_pass)
    if not admin_ok:
        st.sidebar.info("Enter admin passphrase to unlock admin actions.")

if admin_ok:
    st.sidebar.subheader("Maintenance")
    if st.sidebar.button("Run security scan"):
        # run overarching_security.py and show output
        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            proc = subprocess.run(["python", os.path.join(base, "overarching_security.py")], capture_output=True, text=True, cwd=base)
            st.sidebar.text_area("Security scan output", proc.stdout + "\n" + proc.stderr, height=300)
        except Exception as e:
            st.sidebar.error(f"Could not run security scan: {e}")

    if st.sidebar.button("Repair clients CSV"):
        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            proc = subprocess.run(["python", os.path.join(base, "repair_clients_csv.py")], capture_output=True, text=True, cwd=base)
            st.sidebar.text_area("Repair output", proc.stdout + "\n" + proc.stderr, height=200)
        except Exception as e:
            st.sidebar.error(f"Could not run repair script: {e}")

    st.sidebar.markdown("### Sanitize / export")
    if os.path.exists(CLIENTS_CSV):
        try:
            sanitized_df = sanitize_clients(CLIENTS_CSV)
            csv_bytes = sanitized_df.to_csv(index=False).encode("utf-8")
            st.sidebar.download_button("Download sanitized clients CSV", data=csv_bytes, file_name="clients_sanitized.csv")
        except Exception as e:
            st.sidebar.error(f"Could not produce sanitized CSV: {e}")
    else:
        st.sidebar.info("No clients.csv available to sanitize.")


# Keller Williams clients table
st.header("📋 Keller Williams Clients")
if os.path.exists(CLIENTS_CSV):
    try:
        clients_df = pd.read_csv(CLIENTS_CSV)
        st.dataframe(clients_df)
        # Download button for convenience
        csv_bytes = clients_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download clients CSV", data=csv_bytes, file_name="clients.csv")
    except Exception as e:
        st.error(f"Could not read clients file: {e}")
else:
    st.info("No clients.csv found yet. Use the intake form to add leads.")

# Demo deals display (if requested)
if demo_mode and demo_deals_df is not None:
    st.header("💼 Demo Deals")
    try:
        st.dataframe(demo_deals_df)
        demo_csv = demo_deals_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download demo deals CSV", data=demo_csv, file_name="deal_pipeline_demo.csv")
    except Exception as e:
        st.error(f"Could not display demo deals: {e}")

# Home value trends
st.header("📈 Home Value Trends")
if os.path.exists(HOME_VALUE_CSV):
    try:
        chart_data = pd.read_csv(HOME_VALUE_CSV)
        if 'Date' in chart_data.columns:
            chart_data['Date'] = pd.to_datetime(chart_data['Date'], errors='coerce')
            st.line_chart(chart_data.set_index('Date'))
        else:
            st.line_chart(chart_data)
    except Exception as e:
        st.error(f"Could not read home value data: {e}")
else:
    st.info("No home_value.csv found. Add a CSV with Date and Value columns to the data folder.")

# Interior design ideas
st.header("🛋️ Interior Design Ideas")
st.markdown("""
- **Kitchen refresh**: matte black fixtures, quartz countertops  
- **Outdoor lighting**: solar-powered LED path lights  
- **Eco upgrades**: bamboo flooring, low-VOC paint
""")

# Export placeholder
st.download_button("📥 Export Client Slideshow", data="Coming soon...", file_name="client_slideshow.txt")

