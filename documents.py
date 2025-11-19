"""
Document Management Portal

Centralized hub for term sheets, loan packages, client uploads, 
and design gallery from the design/ folder.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
from PIL import Image
import sys

# Add parent to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="Document Management", page_icon="📁", layout="wide")

# Paths
DESIGN_DIR = BASE_DIR / "design"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
DESIGN_DIR.mkdir(exist_ok=True)

# Header
st.title("📁 Document Management Portal")
st.markdown("Centralized document repository for deals, clients, and design assets")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Deal Documents", "🖼️ Design Gallery", "📤 Upload Center", "📊 Document Analytics"])

# Tab 1: Deal Documents
with tab1:
    st.header("Deal Documents Repository")
    st.markdown("Manage term sheets, due diligence, and legal documents")
    
    # Document types
    doc_types = {
        "Term Sheets": "📝",
        "Due Diligence": "🔍",
        "Legal Agreements": "⚖️",
        "Financial Models": "💰",
        "Impact Reports": "📊"
    }
    
    selected_type = st.selectbox("Document Type:", list(doc_types.keys()))
    
    st.subheader(f"{doc_types[selected_type]} {selected_type}")
    
    # Simulated document list (in production, query from database/filesystem)
    documents = [
        {"name": "AgriCo_TermSheet_v2.pdf", "date": "2025-11-15", "size": "245 KB", "deal": "AgriCo"},
        {"name": "HealthApp_DD_Report.pdf", "date": "2025-11-10", "size": "1.2 MB", "deal": "HealthApp"},
        {"name": "CleanWater_Agreement.pdf", "date": "2025-11-08", "size": "567 KB", "deal": "CleanWater Co"},
    ]
    
    if documents:
        df_docs = pd.DataFrame(documents)
        
        # Search/filter
        search = st.text_input("🔍 Search documents:", placeholder="Enter deal name or document title")
        if search:
            df_docs = df_docs[df_docs['name'].str.contains(search, case=False) | 
                              df_docs['deal'].str.contains(search, case=False)]
        
        # Display documents
        for idx, row in df_docs.iterrows():
            with st.expander(f"📄 {row['name']}", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.write(f"**Deal:** {row['deal']}")
                col2.write(f"**Date:** {row['date']}")
                col3.write(f"**Size:** {row['size']}")
                col4.button("⬇️ Download", key=f"dl_{idx}", disabled=True, 
                           help="Document download not implemented")
    else:
        st.info("No documents found for this category")
    
    # Upload section
    st.markdown("---")
    st.subheader("📤 Upload New Document")
    
    col1, col2 = st.columns(2)
    with col1:
        deal_name = st.text_input("Associated Deal:", placeholder="Enter deal name")
    with col2:
        upload_type = st.selectbox("Document Type:", list(doc_types.keys()), key="upload_type")
    
    uploaded_file = st.file_uploader("Choose file:", type=['pdf', 'docx', 'xlsx'])
    
    if uploaded_file and deal_name:
        if st.button("💾 Save Document", type="primary"):
            st.success(f"✅ Document '{uploaded_file.name}' uploaded for {deal_name}")
            st.info("Document indexing and storage not yet implemented")

# Tab 2: Design Gallery
with tab2:
    st.header("🖼️ Design Gallery")
    st.markdown("Client inspiration images and design assets")
    
    # Get all images from design folder
    image_files = list(DESIGN_DIR.glob("*.jpg")) + list(DESIGN_DIR.glob("*.jpeg")) + \
                  list(DESIGN_DIR.glob("*.png")) + list(DESIGN_DIR.glob("*.gif"))
    
    if image_files:
        st.caption(f"Found {len(image_files)} images")
        
        # Grid layout
        cols = st.columns(3)
        for idx, img_path in enumerate(sorted(image_files)):
            with cols[idx % 3]:
                try:
                    img = Image.open(img_path)
                    st.image(img, caption=img_path.name, use_container_width=True)
                    
                    # Metadata
                    file_size = img_path.stat().st_size
                    file_date = datetime.fromtimestamp(img_path.stat().st_mtime)
                    
                    st.caption(f"📅 {file_date.strftime('%Y-%m-%d')} | 💾 {file_size // 1024} KB")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Delete", key=f"del_{idx}"):
                            img_path.unlink()
                            st.rerun()
                    with col2:
                        with open(img_path, "rb") as f:
                            st.download_button("⬇️", f, file_name=img_path.name, key=f"download_{idx}")
                except Exception as e:
                    st.error(f"Error loading {img_path.name}: {e}")
    else:
        st.info("📷 No images in design gallery yet. Upload images in the Client Intake app or use the Upload Center tab.")
        st.markdown("**Tip:** Images uploaded via the Client Intake form will automatically appear here.")

# Tab 3: Upload Center
with tab3:
    st.header("📤 Upload Center")
    st.markdown("Universal file upload for all document types")
    
    upload_category = st.radio(
        "Upload Category:",
        ["Design/Images", "Term Sheets", "Legal Documents", "Financial Models", "Other"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        related_entity = st.text_input("Related To:", 
                                       placeholder="Deal name, client name, or project")
    with col2:
        tags = st.text_input("Tags (comma-separated):", 
                            placeholder="family-first, pet-care, etc.")
    
    notes = st.text_area("Notes:", placeholder="Optional description or context")
    
    # File uploader
    if upload_category == "Design/Images":
        uploaded_files = st.file_uploader(
            "Choose files:",
            type=['jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True
        )
    else:
        uploaded_files = st.file_uploader(
            "Choose files:",
            type=['pdf', 'docx', 'xlsx', 'csv', 'txt'],
            accept_multiple_files=True
        )
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")
        
        if st.button("💾 Upload Files", type="primary"):
            success_count = 0
            for file in uploaded_files:
                if upload_category == "Design/Images":
                    # Save to design folder
                    save_path = DESIGN_DIR / file.name
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())
                    success_count += 1
                else:
                    # For other types, would save to appropriate location
                    st.info(f"Document storage for {upload_category} not yet implemented")
            
            if success_count > 0:
                st.success(f"✅ Uploaded {success_count} file(s) to {upload_category}")
                if upload_category == "Design/Images":
                    st.info("View uploaded images in the Design Gallery tab")

# Tab 4: Document Analytics
with tab4:
    st.header("📊 Document Analytics")
    st.markdown("Usage statistics and document repository insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Count files
    design_count = len(list(DESIGN_DIR.glob("*")))
    
    with col1:
        st.metric("Design Assets", design_count)
    with col2:
        st.metric("Deal Documents", 3, help="Simulated count")
    with col3:
        st.metric("Total Size", "2.1 MB", help="Approximate total storage")
    with col4:
        st.metric("Last Upload", "Today", help="Most recent upload activity")
    
    # Storage by type
    st.subheader("Storage Distribution")
    
    storage_data = pd.DataFrame({
        "Category": ["Design Assets", "Term Sheets", "Due Diligence", "Legal Docs", "Financial Models"],
        "Count": [design_count, 3, 2, 4, 1],
        "Size (MB)": [0.8, 0.5, 1.2, 0.6, 0.3]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(storage_data.set_index("Category")["Count"])
        st.caption("Document count by category")
    
    with col2:
        st.bar_chart(storage_data.set_index("Category")["Size (MB)"])
        st.caption("Storage usage by category (MB)")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    activity = pd.DataFrame({
        "Date": ["2025-11-18", "2025-11-17", "2025-11-15", "2025-11-10"],
        "Action": ["Upload", "Download", "Upload", "Delete"],
        "Document": ["kitchen_design.jpg", "AgriCo_TermSheet_v2.pdf", "HealthApp_DD_Report.pdf", "old_draft.docx"],
        "User": ["System", "Burke Nielsen", "System", "Burke Nielsen"]
    })
    
    st.dataframe(activity, use_container_width=True)

# Sidebar
with st.sidebar:
    st.header("📁 Quick Actions")
    
    if st.button("🔄 Refresh Gallery", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared")
    
    st.markdown("---")
    
    st.header("💾 Storage Info")
    st.metric("Used", "2.1 MB")
    st.metric("Available", "∞", help="Unlimited cloud storage")
    
    st.markdown("---")
    
    with st.expander("ℹ️ About Document Management"):
        st.markdown("""
        **Purpose:** Centralized document repository and asset management
        
        **Features:**
        - Deal document organization (term sheets, DD, legal)
        - Design gallery with image previews
        - Universal upload center
        - Document analytics and usage tracking
        
        **Supported Files:**
        - Images: JPG, PNG, GIF
        - Documents: PDF, DOCX, XLSX, CSV
        
        **Note:** This is a basic implementation. Production systems should include:
        - Version control
        - Access permissions
        - Full-text search
        - Automated backups
        """)
