"""
IRON LADY - COMPLETE STREAMLIT DASHBOARD
Features: Google Sheets, File Upload, OCR, Checklist, Analytics
Team Leaders: Ghazala, Megha, Afreen (Trainee), Soumya (Trainee)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from io import BytesIO
from PIL import Image
import base64

# Try to import optional libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Iron Lady - Sales Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# IRON LADY BRANDING
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
    'warning': '#F77F00',
    'danger': '#D62828',
}

# Custom CSS
st.markdown(f"""
<style>
    .main {{
        background-color: {IRONLADY_COLORS['accent']};
    }}
    .stMetric {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    h1, h2, h3 {{
        color: {IRONLADY_COLORS['secondary']};
        font-weight: 900;
    }}
    .stButton>button {{
        background-color: {IRONLADY_COLORS['primary']};
        color: white;
        font-weight: 900;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 1.1rem;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {IRONLADY_COLORS['danger']};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    .checklist-item {{
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        background: white;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# TEAM LEADERS & CHECKLIST
# ============================================

TEAM_LEADERS = ['Ghazala', 'Megha', 'Afreen', 'Soumya']

DEFAULT_CHECKLIST = [
    {'task': 'WA Audit - Minimum 10', 'priority': 'high'},
    {'task': 'SL Calls - 5', 'priority': 'high'},
    {'task': 'Call Audit - Minimum 5 calls', 'priority': 'medium'},
    {'task': 'CRM Updated', 'priority': 'high'},
    {'task': 'Hot prospects list shared', 'priority': 'high'},
    {'task': 'Follow up calls - 2 Registrations', 'priority': 'high'},
]

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def init_session_state():
    """Initialize session state variables"""
    if 'selected_tl' not in st.session_state:
        st.session_state.selected_tl = None
    if 'checklist' not in st.session_state:
        st.session_state.checklist = {task['task']: False for task in DEFAULT_CHECKLIST}
    if 'uploaded_files_data' not in st.session_state:
        st.session_state.uploaded_files_data = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

@st.cache_resource
def connect_to_google_sheets():
    """Connect to Google Sheets using Streamlit secrets"""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"❌ Google Sheets connection error: {e}")
        return None

@st.cache_data(ttl=300)
def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        client = connect_to_google_sheets()
        if not client:
            return None
        
        # Open spreadsheet by ID or URL
        try:
            if 'docs.google.com' in sheet_id:
                # Extract ID from URL
                sheet_id = sheet_id.split('/d/')[1].split('/')[0]
            spreadsheet = client.open_by_key(sheet_id)
        except Exception as e:
            st.error(f"❌ Could not open spreadsheet. Make sure the sheet is shared with the service account email.")
            return None
        
        data = {}
        worksheets = spreadsheet.worksheets()
        
        for worksheet in worksheets:
            sheet_name = worksheet.title
            records = worksheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                data[sheet_name] = df
        
        return data
        
    except gspread.exceptions.APIError as e:
        st.error(f"❌ API Error: {e}. Check if the sheet is shared with the service account.")
        return None
    except Exception as e:
        st.error(f"❌ Error fetching sheet data: {e}")
        return None

def parse_team_data(sheet_data):
    """Parse team leader data from Google Sheets"""
    if not sheet_data:
        return None
    
    team_data = []
    
    for sheet_name, df in sheet_data.items():
        name_col = None
        for col in df.columns:
            col_upper = str(col).upper()
            if any(keyword in col_upper for keyword in ['RM', 'NAME', 'TEAM', 'LEADER', 'TL']):
                name_col = col
                break
        
        if not name_col:
            continue
        
        for _, row in df.iterrows():
            name = str(row.get(name_col, '')).strip()
            
            if name in TEAM_LEADERS:
                entry = {
                    'name': name,
                    'rms': 0,
                    'pitches_target': 0,
                    'pitches_actual': 0,
                    'reg_target': 0,
                    'reg_actual': 0,
                }
                
                # Extract data with multiple column name variations
                for col in ['Total RMs', 'RMs', 'RM Count', 'Number of RMs', 'Total RM']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['rms'] = int(val)
                            break
                
                for col in ['Target Pitch', 'Pitch Target', 'Target', 'Pitch Goal']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['pitches_target'] = int(val)
                            break
                
                for col in ['Actual Pitch', 'Pitch Actual', 'Achieved', 'Pitches']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['pitches_actual'] = int(val)
                            break
                
                for col in ['Target Registration', 'Registration Target', 'Target Reg']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['reg_target'] = int(val)
                            break
                
                for col in ['Actual Registration', 'Registration Actual', 'Actual Reg', 'Registrations']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['reg_actual'] = int(val)
                            break
                
                # Calculate metrics
                if entry['pitches_target'] > 0:
                    entry['pitch_achievement'] = round((entry['pitches_actual'] / entry['pitches_target']) * 100, 1)
                else:
                    entry['pitch_achievement'] = 0
                
                if entry['reg_target'] > 0:
                    entry['reg_achievement'] = round((entry['reg_actual'] / entry['reg_target']) * 100, 1)
                else:
                    entry['reg_achievement'] = 0
                
                if entry['pitches_actual'] > 0:
                    entry['conversion'] = round((entry['reg_actual'] / entry['pitches_actual']) * 100, 1)
                else:
                    entry['conversion'] = 0
                
                team_data.append(entry)
    
    return team_data if team_data else None

# ============================================
# FILE UPLOAD & OCR
# ============================================

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    file_data = {
        'filename': uploaded_file.name,
        'type': uploaded_file.type,
        'size': uploaded_file.size,
        'text': '',
        'uploaded_at': datetime.now()
    }
    
    try:
        if uploaded_file.type == 'application/pdf':
            if OCR_AVAILABLE:
                images = convert_from_bytes(uploaded_file.read())
                text = ''
                for img in images:
                    text += pytesseract.image_to_string(img)
                file_data['text'] = text
            else:
                file_data['text'] = "OCR not available. Install pytesseract and pdf2image."
        
        elif uploaded_file.type.startswith('image/'):
            if OCR_AVAILABLE:
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image)
                file_data['text'] = text
            else:
                file_data['text'] = "OCR not available. Install pytesseract."
        
        elif uploaded_file.type == 'text/plain':
            file_data['text'] = uploaded_file.read().decode('utf-8')
        
        else:
            file_data['text'] = "Unsupported file type"
        
    except Exception as e:
        file_data['text'] = f"Error processing file: {e}"
    
    return file_data

# ============================================
# SAMPLE DATA
# ============================================

def get_sample_data():
    """Sample data for demo"""
    return [
        {
            'name': 'Ghazala',
            'rms': 5,
            'pitches_target': 30,
            'pitches_actual': 28,
            'pitch_achievement': 93.3,
            'reg_target': 22,
            'reg_actual': 20,
            'reg_achievement': 90.9,
            'conversion': 71.4
        },
        {
            'name': 'Megha',
            'rms': 4,
            'pitches_target': 15,
            'pitches_actual': 13,
            'pitch_achievement': 86.7,
            'reg_target': 12,
            'reg_actual': 11,
            'reg_achievement': 91.7,
            'conversion': 84.6
        },
        {
            'name': 'Afreen',
            'rms': 3,
            'pitches_target': 10,
            'pitches_actual': 9,
            'pitch_achievement': 90.0,
            'reg_target': 8,
            'reg_actual': 6,
            'reg_achievement': 75.0,
            'conversion': 66.7
        },
        {
            'name': 'Soumya',
            'rms': 3,
            'pitches_target': 10,
            'pitches_actual': 8,
            'pitch_achievement': 80.0,
            'reg_target': 7,
            'reg_actual': 5,
            'reg_achievement': 71.4,
            'conversion': 62.5
        }
    ]

# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_status_color(percentage):
    if percentage >= 90:
        return IRONLADY_COLORS['success']
    elif percentage >= 75:
        return IRONLADY_COLORS['warning']
    else:
        return IRONLADY_COLORS['danger']

def get_status_text(percentage):
    if percentage >= 90:
        return "Excellent 🎯"
    elif percentage >= 75:
        return "Good ✅"
    elif percentage >= 60:
        return "Fair ⚠️"
    else:
        return "Needs Attention ❌"

# ============================================
# PAGE: DASHBOARD
# ============================================

def show_dashboard(df):
    """Main dashboard view"""
    
    if st.session_state.selected_tl:
        # Individual TL Dashboard
        tl_name = st.session_state.selected_tl
        tl_data = df[df['name'] == tl_name].iloc[0]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['primary']}; margin-bottom: 25px;">
            <h2 style="margin: 0; color: {IRONLADY_COLORS['primary']};">👤 {tl_name}'s Performance Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💼 RMs", tl_data['rms'])
        
        with col2:
            st.metric(
                "🎯 Pitch Achievement",
                f"{tl_data['pitch_achievement']:.1f}%",
                f"{tl_data['pitches_actual']}/{tl_data['pitches_target']}"
            )
        
        with col3:
            st.metric(
                "📝 Registration Achievement",
                f"{tl_data['reg_achievement']:.1f}%",
                f"{tl_data['reg_actual']}/{tl_data['reg_target']}"
            )
        
        with col4:
            st.metric(
                "💯 Conversion Rate",
                f"{tl_data['conversion']:.1f}%"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Achievement Overview")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Pitch', 'Registration'],
                y=[tl_data['pitch_achievement'], tl_data['reg_achievement']],
                marker_color=[IRONLADY_COLORS['success'], IRONLADY_COLORS['warning']],
                text=[f"{tl_data['pitch_achievement']:.1f}%", f"{tl_data['reg_achievement']:.1f}%"],
                textposition='outside'
            ))
            fig.update_layout(height=400, yaxis_range=[0, 110])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Progress Details")
            progress_df = pd.DataFrame({
                'Metric': ['Pitches', 'Registrations'],
                'Target': [tl_data['pitches_target'], tl_data['reg_target']],
                'Actual': [tl_data['pitches_actual'], tl_data['reg_actual']],
                'Achievement': [f"{tl_data['pitch_achievement']:.1f}%", f"{tl_data['reg_achievement']:.1f}%"]
            })
            st.dataframe(progress_df, use_container_width=True, hide_index=True)
    
    else:
        # Team Overview Dashboard
        st.markdown(f"""
        <div style="padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['warning']}; margin-bottom: 30px;">
            <h3 style="margin: 0;">👋 Welcome! Select your name to access your dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👥 TEAM LEADERS")
        
        col1, col2 = st.columns(2)
        
        for idx, tl in enumerate(TEAM_LEADERS):
            role = "Senior TL" if tl in ['Ghazala', 'Megha'] else "TL Trainee"
            icon = "🏆" if tl in ['Ghazala', 'Megha'] else "🌟"
            
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"{icon} {tl.upper()} ({role})", key=f"tl_{tl}", use_container_width=True):
                    st.session_state.selected_tl = tl
                    st.rerun()
        
        st.markdown("---")
        
        # Overall Metrics
        total_rms = df['rms'].sum()
        total_pitch_target = df['pitches_target'].sum()
        total_pitch_actual = df['pitches_actual'].sum()
        total_reg_target = df['reg_target'].sum()
        total_reg_actual = df['reg_actual'].sum()
        
        overall_pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
        overall_reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
        overall_conversion = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
        
        st.markdown("### 📊 OVERALL TEAM PERFORMANCE")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💼 Total RMs", total_rms)
        
        with col2:
            st.metric("🎯 Pitch Achievement", f"{overall_pitch_achievement:.1f}%", f"{total_pitch_actual}/{total_pitch_target}")
        
        with col3:
            st.metric("📝 Registration Achievement", f"{overall_reg_achievement:.1f}%", f"{total_reg_actual}/{total_reg_target}")
        
        with col4:
            st.metric("💯 Conversion Rate", f"{overall_conversion:.1f}%")
        
        st.markdown("---")
        
        # Team Table
        st.markdown("### 📈 DETAILED TEAM PERFORMANCE")
        
        display_df = df.copy()
        display_df['Pitches'] = display_df.apply(lambda x: f"{x['pitches_actual']}/{x['pitches_target']}", axis=1)
        display_df['Registrations'] = display_df.apply(lambda x: f"{x['reg_actual']}/{x['reg_target']}", axis=1)
        display_df['Conversion'] = display_df['conversion'].apply(lambda x: f"{x:.1f}%")
        
        table_df = display_df[['name', 'rms', 'Pitches', 'Registrations', 'Conversion']]
        table_df.columns = ['Team Leader', 'RMs', 'Pitches', 'Registrations', 'Conversion']
        
        st.dataframe(table_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Conversion Comparison")
            fig = px.bar(df, x='name', y='conversion', color='conversion',
                        color_continuous_scale=['#D62828', '#F77F00', '#2A9D8F'])
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Achievement Comparison")
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Pitch', x=df['name'], y=df['pitch_achievement'], marker_color=IRONLADY_COLORS['success']))
            fig.add_trace(go.Bar(name='Registration', x=df['name'], y=df['reg_achievement'], marker_color=IRONLADY_COLORS['warning']))
            fig.update_layout(barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE: CHECKLIST
# ============================================

def show_checklist():
    """Daily checklist page"""
    st.markdown(f"""
    <div style="text-align: center; padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['primary']}; margin-bottom: 25px;">
        <h2 style="margin: 0; color: {IRONLADY_COLORS['primary']};">✅ DAILY CHECKLIST</h2>
    </div>
    """, unsafe_allow_html=True)
    
    completed = sum(1 for v in st.session_state.checklist.values() if v)
    total = len(st.session_state.checklist)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    st.progress(completion_rate / 100, text=f"Progress: {completed}/{total} tasks ({completion_rate:.0f}%)")
    
    st.markdown("---")
    
    for task_item in DEFAULT_CHECKLIST:
        task = task_item['task']
        priority = task_item['priority']
        
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            checked = st.checkbox("", value=st.session_state.checklist[task], key=f"check_{task}", label_visibility="collapsed")
            st.session_state.checklist[task] = checked
        
        with col2:
            priority_icon = "🔴" if priority == "high" else "🟡"
            status_icon = "✅" if checked else "⏳"
            st.markdown(f"{status_icon} {priority_icon} **{task}**")
    
    st.markdown("---")
    
    if st.button("🔄 Reset Checklist", use_container_width=True):
        st.session_state.checklist = {task['task']: False for task in DEFAULT_CHECKLIST}
        st.rerun()

# ============================================
# PAGE: FILE UPLOAD
# ============================================

def show_file_upload():
    """File upload and OCR page"""
    st.markdown(f"""
    <div style="text-align: center; padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['primary']}; margin-bottom: 25px;">
        <h2 style="margin: 0; color: {IRONLADY_COLORS['primary']};">📁 FILE UPLOAD & DOCUMENT ANALYSIS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not OCR_AVAILABLE:
        st.warning("⚠️ OCR features require `pytesseract` and `pdf2image`. Some features may be limited.")
    
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, Images, Text files)",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        accept_multiple_files=True,
        help="Upload attendance sheets, reports, or any documents for analysis"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                file_data = process_uploaded_file(uploaded_file)
                st.session_state.uploaded_files_data.append(file_data)
        
        st.success(f"✅ Processed {len(uploaded_files)} file(s)")
    
    if st.session_state.uploaded_files_data:
        st.markdown("---")
        st.markdown("### 📊 Uploaded Files")
        
        for idx, file_data in enumerate(st.session_state.uploaded_files_data):
            with st.expander(f"📄 {file_data['filename']} ({file_data['size']} bytes)"):
                st.markdown(f"**Type:** {file_data['type']}")
                st.markdown(f"**Uploaded:** {file_data['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if file_data['text']:
                    st.markdown("**Extracted Text:**")
                    st.text_area("", file_data['text'][:1000], height=200, key=f"text_{idx}", label_visibility="collapsed")
                    
                    if len(file_data['text']) > 1000:
                        st.info(f"Showing first 1000 characters. Total: {len(file_data['text'])} characters")
        
        if st.button("🗑️ Clear All Files", use_container_width=True):
            st.session_state.uploaded_files_data = []
            st.rerun()

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    init_session_state()
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 50px 30px; background: {IRONLADY_COLORS['accent']}; border-top: 8px solid {IRONLADY_COLORS['primary']}; border-bottom: 8px solid {IRONLADY_COLORS['primary']}; margin-bottom: 30px;">
        <h1 style="font-size: 4rem; margin: 0; letter-spacing: 8px; color: {IRONLADY_COLORS['secondary']};">IRON LADY</h1>
        <div style="background: {IRONLADY_COLORS['primary']}; height: 4px; width: 150px; margin: 20px auto;"></div>
        <p style="font-size: 1.3rem; margin: 0; color: {IRONLADY_COLORS['secondary']}; font-weight: 600;">Sales Performance Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ NAVIGATION")
        
        page = st.radio(
            "",
            ["📊 Dashboard", "✅ Checklist", "📁 File Upload"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox("📈 Use Google Sheets", value=True)
        
        sheet_id = None
        if use_sheets:
            try:
                sheet_id = st.secrets.get("google_sheet_id", None)
                if sheet_id:
                    st.success("✅ Sheet ID configured")
                    
                    # Show service account email for sharing
                    try:
                        service_email = st.secrets["gcp_service_account"]["client_email"]
                        with st.expander("📧 Service Account Email"):
                            st.code(service_email, language=None)
                            st.caption("Share your Google Sheet with this email")
                    except:
                        pass
                else:
                    sheet_id = st.text_input("Google Sheet ID or URL", placeholder="1abc123xyz...")
            except:
                sheet_id = st.text_input("Google Sheet ID or URL", placeholder="1abc123xyz...")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.info(f"**⏰ Updated**\n{datetime.now().strftime('%I:%M %p')}")
        
        st.markdown("---")
        st.markdown("### 👥 TEAM")
        st.markdown("🏆 Ghazala\n🏆 Megha\n🌟 Afreen\n🌟 Soumya")
        
        if st.session_state.selected_tl:
            st.markdown("---")
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state.selected_tl = None
                st.rerun()
    
    # Fetch Data
    team_data = None
    data_source = "📝 Sample Data"
    
    if use_sheets and sheet_id:
        with st.spinner("📊 Loading from Google Sheets..."):
            sheet_data = fetch_sheet_data(sheet_id)
            if sheet_data:
                team_data = parse_team_data(sheet_data)
                if team_data:
                    data_source = "📊 Google Sheets (Live)"
                    st.success(f"✅ Loaded {len(team_data)} team leaders")
    
    if not team_data:
        team_data = get_sample_data()
    
    df = pd.DataFrame(team_data)
    
    # Data Source Badge
    badge_color = '#d4edda' if 'Live' in data_source else '#fff3cd'
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: {badge_color}; border-radius: 10px; margin-bottom: 20px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
        <strong>📊 Source:</strong> {data_source} | <strong>🕐 Updated:</strong> {datetime.now().strftime('%I:%M %p')}
    </div>
    """, unsafe_allow_html=True)
    
    # Page Routing
    if page == "📊 Dashboard":
        show_dashboard(df)
    elif page == "✅ Checklist":
        show_checklist()
    elif page == "📁 File Upload":
        show_file_upload()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: {IRONLADY_COLORS['accent']}; border-radius: 12px; border-top: 4px solid {IRONLADY_COLORS['primary']};">
        <p style="margin: 0; font-weight: 900; font-size: 1.8rem; color: {IRONLADY_COLORS['secondary']};">IRON LADY</p>
        <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.7;">© 2024 Iron Lady. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
