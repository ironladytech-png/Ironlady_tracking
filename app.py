"""
IRON LADY SALES TRACKER - GOOGLE SHEETS INTEGRATED VERSION
Automatically pulls data from Google Sheets filled via Google Forms
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Try to import Google Sheets library
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    st.warning("⚠️ Google Sheets integration not available. Install: pip install gspread google-auth")

# ============================================
# OFFICIAL IRON LADY COMPANY COLORS
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
    'warning': '#F77F00',
    'danger': '#D62828',
    'light': '#FAF3E0',
    'dark': '#1A1A1A',
    'white': '#FFFFFF',
}

# ============================================
# PAGE CONFIG & SETUP
# ============================================

st.set_page_config(
    page_title="Iron Lady Sales Tracker | Google Sheets Integrated",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [Previous CSS remains the same - using same styling]
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    
    .logo-container {{
        text-align: center;
        padding: 30px 20px;
        background: {IRONLADY_COLORS['accent']};
        border-radius: 0px;
        margin-bottom: 30px;
        border-top: 5px solid {IRONLADY_COLORS['primary']};
        border-bottom: 5px solid {IRONLADY_COLORS['primary']};
    }}
    
    .logo-text {{
        color: {IRONLADY_COLORS['dark']};
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: 3px;
        margin: 0;
        text-transform: uppercase;
    }}
    
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 0px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .success-msg {{ 
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: {IRONLADY_COLORS['success']}; 
        padding: 15px 20px; 
        border-radius: 0px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['success']};
        font-weight: 500;
    }}
    
    .error-msg {{ 
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: {IRONLADY_COLORS['danger']}; 
        padding: 15px 20px; 
        border-radius: 0px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['danger']};
        font-weight: 500;
    }}
    
    .info-msg {{
        background: {IRONLADY_COLORS['accent']};
        color: {IRONLADY_COLORS['dark']};
        padding: 15px 20px;
        border-radius: 0px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        font-weight: 500;
    }}
    
    .stButton > button {{
        background: {IRONLADY_COLORS['primary']};
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 0px;
        font-weight: 700;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stButton > button:hover {{
        background: {IRONLADY_COLORS['gradient_end']};
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);
        transform: translateY(-2px);
    }}
    
    h2, h3 {{
        color: {IRONLADY_COLORS['dark']};
        font-weight: 900;
        border-bottom: 4px solid {IRONLADY_COLORS['primary']};
        padding-bottom: 10px;
        margin-top: 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'team_leads' not in st.session_state:
    st.session_state.team_leads = [
        'Priya Sharma',
        'Rahul Mehta',
        'Anjali Desai',
        'Vikram Singh',
        'Neha Patel'
    ]

if 'user' not in st.session_state:
    st.session_state.user = None

if 'gsheet_data' not in st.session_state:
    st.session_state.gsheet_data = None

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None

if 'checklist' not in st.session_state:
    st.session_state.checklist = {}

if 'files_uploaded' not in st.session_state:
    st.session_state.files_uploaded = {}

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = 'Day 1-1'

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# ============================================
# GOOGLE SHEETS INTEGRATION
# ============================================

def connect_to_google_sheets():
    """Connect to Google Sheets using credentials"""
    try:
        # Method 1: Using Streamlit secrets (for deployment)
        if 'gcp_service_account' in st.secrets:
            credentials_dict = dict(st.secrets["gcp_service_account"])
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
            )
            client = gspread.authorize(credentials)
            return client
        
        # Method 2: Using service account file (for local development)
        elif os.path.exists('credentials.json'):
            credentials = Credentials.from_service_account_file(
                'credentials.json',
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
            )
            client = gspread.authorize(credentials)
            return client
        
        else:
            st.error("❌ Google Sheets credentials not found. Please configure.")
            return None
            
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
        return None

def fetch_google_sheet_data(sheet_url_or_id):
    """Fetch data from Google Sheets"""
    try:
        client = connect_to_google_sheets()
        if not client:
            return None
        
        # Open the spreadsheet
        try:
            # Try opening by URL first
            spreadsheet = client.open_by_url(sheet_url_or_id)
        except:
            # Try opening by ID
            spreadsheet = client.open_by_key(sheet_url_or_id)
        
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        
        data = {}
        for worksheet in worksheets:
            sheet_name = worksheet.title
            # Get all values as DataFrame
            records = worksheet.get_all_records()
            if records:
                data[sheet_name] = pd.DataFrame(records)
        
        return data
        
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return None

def parse_wa_audits_data(df):
    """Parse WA Audits data from Google Sheets"""
    try:
        # Expected columns: Target, Achieved, RM Name, Count, Good, Bad
        parsed_data = []
        
        for _, row in df.iterrows():
            if pd.notna(row.get('RM Name', '')):
                rm_name = str(row.get('RM Name', '')).strip()
                if rm_name and not rm_name.startswith('#'):  # Skip header rows
                    parsed_data.append({
                        'RM_Name': rm_name,
                        'WA_Target': int(row.get('Target', 0)) if pd.notna(row.get('Target')) else 0,
                        'WA_Achieved': int(row.get('Achieved', 0)) if pd.notna(row.get('Achieved')) else 0,
                        'WA_Count': int(row.get('Count', 0)) if pd.notna(row.get('Count')) else 0,
                        'WA_Good': int(row.get('Good', 0)) if pd.notna(row.get('Good')) else 0,
                        'WA_Bad': int(row.get('Bad', 0)) if pd.notna(row.get('Bad')) else 0,
                    })
        
        return pd.DataFrame(parsed_data) if parsed_data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error parsing WA Audits: {str(e)}")
        return pd.DataFrame()

def parse_call_audits_data(df):
    """Parse Call Audits data from Google Sheets"""
    try:
        parsed_data = []
        
        for _, row in df.iterrows():
            if pd.notna(row.get('RM Name', '')):
                rm_name = str(row.get('RM Name', '')).strip()
                if rm_name and not rm_name.startswith('#'):
                    parsed_data.append({
                        'RM_Name': rm_name,
                        'Call_Target': int(row.get('Target', 0)) if pd.notna(row.get('Target')) else 0,
                        'Call_Achieved': int(row.get('Achieved', 0)) if pd.notna(row.get('Achieved')) else 0,
                        'Call_Count': int(row.get('Count', 0)) if pd.notna(row.get('Count')) else 0,
                        'Call_Good': int(row.get('Good', 0)) if pd.notna(row.get('Good')) else 0,
                        'Call_Bad': int(row.get('Bad', 0)) if pd.notna(row.get('Bad')) else 0,
                    })
        
        return pd.DataFrame(parsed_data) if parsed_data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error parsing Call Audits: {str(e)}")
        return pd.DataFrame()

def parse_mock_calls_data(df):
    """Parse Mock Calls data from Google Sheets"""
    try:
        parsed_data = []
        
        for _, row in df.iterrows():
            if pd.notna(row.get('RM Name', '')):
                rm_name = str(row.get('RM Name', '')).strip()
                if rm_name and not rm_name.startswith('#'):
                    parsed_data.append({
                        'RM_Name': rm_name,
                        'Mock_Target': int(row.get('Target', 0)) if pd.notna(row.get('Target')) else 0,
                        'Mock_Achieved': int(row.get('Achieved', 0)) if pd.notna(row.get('Achieved')) else 0,
                        'Mock_Count': int(row.get('Count', 0)) if pd.notna(row.get('Count')) else 0,
                        'Mock_Topic': str(row.get('Topic', '')) if pd.notna(row.get('Topic')) else '',
                        'Mock_Task': str(row.get('Task Assigned / Practice', '')) if pd.notna(row.get('Task Assigned / Practice')) else '',
                    })
        
        return pd.DataFrame(parsed_data) if parsed_data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error parsing Mock Calls: {str(e)}")
        return pd.DataFrame()

def combine_sheet_data(gsheet_data):
    """Combine all sheets data into unified format"""
    try:
        # Parse each sheet type
        wa_df = pd.DataFrame()
        call_df = pd.DataFrame()
        mock_df = pd.DataFrame()
        
        for sheet_name, df in gsheet_data.items():
            sheet_lower = sheet_name.lower()
            
            if 'wa' in sheet_lower or 'whatsapp' in sheet_lower:
                wa_df = parse_wa_audits_data(df)
            elif 'call' in sheet_lower:
                call_df = parse_call_audits_data(df)
            elif 'mock' in sheet_lower:
                mock_df = parse_mock_calls_data(df)
        
        # Combine all data by RM Name
        if not wa_df.empty:
            combined = wa_df
            
            if not call_df.empty:
                combined = combined.merge(call_df, on='RM_Name', how='outer')
            
            if not mock_df.empty:
                combined = combined.merge(mock_df, on='RM_Name', how='outer')
            
            # Fill NaN values with 0
            combined = combined.fillna(0)
            
            return combined
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error combining sheet data: {str(e)}")
        return pd.DataFrame()

# ============================================
# LOGIN SECTION
# ============================================

def show_login_page():
    """Display login page"""
    st.markdown(f"""
    <div class="logo-container">
        <h1 class="logo-text">IRON LADY</h1>
        <p class="logo-tagline">Sales Performance Management System - Google Sheets Integrated</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="info-msg">👋 <strong>Welcome!</strong> Select your name to access your dashboard</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("### 👥 TEAM LEADERS")
        
        cols = st.columns(2)
        for idx, lead in enumerate(st.session_state.team_leads):
            with cols[idx % 2]:
                if st.button(f"👤 {lead}", key=f"login_{idx}", use_container_width=True):
                    st.session_state.user = lead
                    st.session_state.checklist = {}
                    st.rerun()

# ============================================
# GOOGLE SHEETS CONFIG SECTION
# ============================================

def show_google_sheets_config():
    """Show Google Sheets configuration interface"""
    st.markdown("### 🔗 GOOGLE SHEETS CONNECTION")
    
    st.markdown('<div class="info-msg">📊 Connect your Google Form responses sheet to automatically pull RM data.</div>', unsafe_allow_html=True)
    
    # Input for Google Sheets URL or ID
    sheet_url = st.text_input(
        "Google Sheets URL or ID",
        placeholder="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit or just YOUR_SHEET_ID",
        help="Paste your Google Sheets URL or just the Sheet ID"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 SYNC DATA", use_container_width=True, type="primary"):
            if sheet_url:
                with st.spinner("Syncing data from Google Sheets..."):
                    data = fetch_google_sheet_data(sheet_url)
                    
                    if data:
                        st.session_state.gsheet_data = data
                        st.session_state.last_sync = datetime.now()
                        st.markdown('<div class="success-msg">✅ Data synced successfully!</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown('<div class="error-msg">❌ Failed to sync data. Check credentials and sheet URL.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ Please enter a Google Sheets URL or ID</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.last_sync:
            time_ago = datetime.now() - st.session_state.last_sync
            minutes_ago = int(time_ago.total_seconds() / 60)
            st.info(f"Last synced: {minutes_ago} minutes ago")

# ============================================
# MAIN APP
# ============================================

def main():
    if st.session_state.user is None:
        show_login_page()
        return
    
    # Header
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"""
        <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-radius: 0px; border-left: 5px solid {IRONLADY_COLORS['primary']};">
            <h2 style="margin: 0; color: {IRONLADY_COLORS['dark']}; border: none; font-weight: 900; text-transform: uppercase;">🏆 IRON LADY</h2>
            <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.8;">Team Leader: <strong>{st.session_state.user}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 0px; border-left: 5px solid {IRONLADY_COLORS['primary']};">
            <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem;">📅 <strong>Date:</strong> {st.session_state.selected_date.strftime('%B %d, %Y')}</p>
            <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem;">📊 <strong>Session:</strong> {st.session_state.selected_day}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ DASHBOARD SETTINGS")
        
        st.session_state.selected_day = st.selectbox(
            "📊 Select Day Type",
            options=['Day 1-1', 'Day 1', 'Day 2'],
            index=['Day 1-1', 'Day 1', 'Day 2'].index(st.session_state.selected_day)
        )
        
        st.session_state.selected_date = st.date_input(
            "📅 Select Date",
            value=st.session_state.selected_date
        )
        
        st.markdown("---")
        
        if st.session_state.last_sync:
            st.success(f"✅ Data synced")
            time_ago = datetime.now() - st.session_state.last_sync
            st.caption(f"🕐 {int(time_ago.total_seconds() / 60)} min ago")
        else:
            st.warning("⚠️ No data synced")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "🔗 GOOGLE SHEETS SYNC",
        "📊 PERFORMANCE DASHBOARD", 
        "✅ DAILY CHECKLIST"
    ])
    
    with tab1:
        show_google_sheets_config()
        
        if st.session_state.gsheet_data:
            st.markdown("### 📋 SYNCED DATA PREVIEW")
            
            for sheet_name, df in st.session_state.gsheet_data.items():
                with st.expander(f"📄 {sheet_name} ({len(df)} rows)"):
                    st.dataframe(df, use_container_width=True)
            
            # Show combined data
            combined_df = combine_sheet_data(st.session_state.gsheet_data)
            if not combined_df.empty:
                st.markdown("### 📊 COMBINED RM DATA")
                st.dataframe(combined_df, use_container_width=True)
    
    with tab2:
        if st.session_state.gsheet_data:
            combined_df = combine_sheet_data(st.session_state.gsheet_data)
            
            if not combined_df.empty:
                st.markdown("### 📊 TEAM PERFORMANCE DASHBOARD")
                
                # Summary metrics
                total_rms = len(combined_df)
                total_wa = combined_df['WA_Achieved'].sum() if 'WA_Achieved' in combined_df.columns else 0
                total_calls = combined_df['Call_Achieved'].sum() if 'Call_Achieved' in combined_df.columns else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total RMs", total_rms)
                with col2:
                    st.metric("WA Audits Completed", int(total_wa))
                with col3:
                    st.metric("Call Audits Completed", int(total_calls))
                
                st.markdown("---")
                st.dataframe(combined_df, use_container_width=True, hide_index=True)
            else:
                st.info("📊 No data available. Please sync Google Sheets data first.")
        else:
            st.info("🔗 Please connect and sync your Google Sheets in the first tab.")
    
    with tab3:
        st.markdown("### ✅ DAILY CHECKLIST")
        st.info("Checklist feature - same as before")

if __name__ == "__main__":
    if not GSHEETS_AVAILABLE:
        st.error("❌ Google Sheets integration requires: pip install gspread google-auth")
        st.stop()
    
    main()
