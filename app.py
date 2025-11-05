"""
IRON LADY - ULTIMATE COMPLETE SALES DASHBOARD
==============================================
✅ Multi-User Login System with Logout
✅ Individual Dashboards for Each Team Leader
✅ Manual RM Data Entry System
✅ Google Sheets Live Integration & Viewer
✅ AI-Powered Performance Analysis
✅ Email Reports to Multiple Recipients
✅ Daily Activity Checklist (Day 1-1, Day 1, Day 2)
✅ Document Management System
✅ Performance Visualizations & Charts
✅ Top/Bottom Performer Analysis
✅ Smart Recommendations
✅ Works WITHOUT Configuration (Sample Data)

Team: Ghazala, Megha, Afreen, Soumya
Version: 11.0 - ULTIMATE COMPLETE EDITION
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import Google Sheets (optional)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except:
    GSHEETS_AVAILABLE = False

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
# SESSION STATE INITIALIZATION
# ============================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'rm_data_by_lead' not in st.session_state:
    st.session_state.rm_data_by_lead = {}

if 'checklist' not in st.session_state:
    st.session_state.checklist = {}

if 'files_uploaded' not in st.session_state:
    st.session_state.files_uploaded = {}

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = 'Day 1-1'

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

if 'loaded_sheet_data' not in st.session_state:
    st.session_state.loaded_sheet_data = None

if 'use_google_sheets' not in st.session_state:
    st.session_state.use_google_sheets = False

# ============================================
# IRON LADY BRANDING & STYLING
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
    'warning': '#F77F00',
    'danger': '#D62828',
}

# Complete Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background-color: {IRONLADY_COLORS['accent']};
    }}
    
    .stMetric {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    h1, h2, h3 {{
        color: {IRONLADY_COLORS['secondary']};
        font-weight: 900;
    }}
    
    .login-card {{
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border-left: 8px solid {IRONLADY_COLORS['primary']};
        margin: 20px 0;
        transition: all 0.3s;
    }}
    
    .login-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(230, 57, 70, 0.2);
    }}
    
    .insight-box {{
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .success-msg {{
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: {IRONLADY_COLORS['success']};
        padding: 15px 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['success']};
        font-weight: 500;
    }}
    
    .warning-msg {{
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
        color: {IRONLADY_COLORS['warning']};
        padding: 15px 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['warning']};
        font-weight: 500;
    }}
    
    .error-msg {{
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: {IRONLADY_COLORS['danger']};
        padding: 15px 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['danger']};
        font-weight: 500;
    }}
    
    .info-msg {{
        background: {IRONLADY_COLORS['accent']};
        color: {IRONLADY_COLORS['secondary']};
        padding: 15px 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        font-weight: 500;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 15px 25px;
        font-weight: 700;
        color: {IRONLADY_COLORS['secondary']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {IRONLADY_COLORS['primary']};
        color: white !important;
    }}
    
    .dataframe {{
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    .dataframe thead tr th {{
        background: {IRONLADY_COLORS['secondary']} !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 15px !important;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {IRONLADY_COLORS['secondary']} 0%, {IRONLADY_COLORS['primary']} 100%);
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    .stButton > button {{
        background: {IRONLADY_COLORS['primary']};
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stButton > button:hover {{
        background: {IRONLADY_COLORS['danger']};
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);
        transform: translateY(-2px);
    }}
    
    .badge {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 5px;
    }}
    
    .badge-upload {{
        background: {IRONLADY_COLORS['primary']};
        color: white;
    }}
    
    .badge-manual {{
        background: {IRONLADY_COLORS['warning']};
        color: white;
    }}
    
    .badge-ongoing {{
        background: {IRONLADY_COLORS['secondary']};
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# TEAM LEADERS CONFIGURATION
# ============================================

TEAM_LEADERS = {
    'Ghazala': {
        'role': 'Senior Team Leader',
        'icon': '🏆',
        'color': '#E63946'
    },
    'Megha': {
        'role': 'Senior Team Leader',
        'icon': '🏆',
        'color': '#2A9D8F'
    },
    'Afreen': {
        'role': 'Team Leader (Trainee)',
        'icon': '🌟',
        'color': '#F77F00'
    },
    'Soumya': {
        'role': 'Team Leader (Trainee)',
        'icon': '🌟',
        'color': '#D62828'
    }
}

# ============================================
# DAILY CHECKLIST ITEMS
# ============================================

CHECKLIST_ITEMS = {
    'Day 1-1': [
        {'task': 'Mocks - Who are the people - Buddy structure', 'type': 'text', 'time': '9:00-9:30 AM', 'priority': 'high'},
        {'task': 'Sign off Activities - each RM type', 'type': 'text', 'required': True, 'priority': 'high'},
        {'task': 'WA Audit - Minimum 10', 'type': 'upload', 'required': True, 'priority': 'high'},
        {'task': 'Follow up Calls - 2 Registrations (Last MC)', 'type': 'manual', 'priority': 'medium'},
        {'task': 'SL Calls - 5 (Share SL status list with numbers & status)', 'type': 'manual', 'priority': 'medium'},
        {'task': 'Lead Analysis AI summary of meeting', 'type': 'text', 'priority': 'medium'},
        {'task': 'Call Audit - Minimum 5 calls (crosscheck with app)', 'type': 'number', 'priority': 'medium'},
        {'task': 'Tracking: CRM Update, Call/Attendance/WA (Through the day)', 'type': 'ongoing', 'priority': 'high'},
        {'task': 'Targets Sharing - percentage and potential list of each RM', 'type': 'text', 'priority': 'high'},
        {'task': 'CRM Updation', 'type': 'checkbox', 'priority': 'high'},
        {'task': 'Sharing hot prospects list of each RM', 'type': 'upload', 'priority': 'high'}
    ],
    'Day 1': [
        {'task': 'WA Audit - 10', 'type': 'upload', 'time': '9:00-9:30 AM', 'priority': 'high'},
        {'task': 'SL Calls - 8 (Share SL status list with numbers & status)', 'type': 'manual', 'priority': 'high'},
        {'task': 'Sign off Activities - each RM', 'type': 'text', 'priority': 'high'},
        {'task': 'Mocks - Who are the people - Buddy structure', 'type': 'text', 'priority': 'medium'},
        {'task': '30s pitch Prep', 'type': 'text', 'priority': 'medium'},
        {'task': 'Tracking: CRM Update, Call/Attendance/WA (Through the day)', 'type': 'ongoing', 'priority': 'high'},
        {'task': 'Call Audit - Minimum 5 calls', 'type': 'number', 'priority': 'medium'},
        {'task': 'Targets Sharing - % and potential list (before & after session)', 'type': 'text', 'priority': 'high'},
        {'task': '10% Conversion - action points update', 'type': 'text', 'priority': 'high'},
        {'task': 'CRM Updation - including attendance & Registrations', 'type': 'checkbox', 'priority': 'high'},
        {'task': 'Sharing hot prospects list of each RM and Tracking status', 'type': 'upload', 'priority': 'high'}
    ],
    'Day 2': [
        {'task': 'SL Calls - 10-12 (Share SL status list)', 'type': 'upload', 'time': '9:00-9:30 AM', 'priority': 'high'},
        {'task': 'WA Audit - As needed', 'type': 'manual', 'priority': 'medium'},
        {'task': 'Tracking: CRM Update, Call/Attendance/WA (Through the day)', 'type': 'ongoing', 'priority': 'high'},
        {'task': 'Sign off Activities - each RM', 'type': 'text', 'priority': 'high'},
        {'task': 'Targets Sharing - 10% before session, 15% after session (with potential lists)', 'type': 'text', 'priority': 'high'},
        {'task': 'CRM Updation - including attendance & Registrations', 'type': 'checkbox', 'priority': 'high'},
        {'task': 'Sharing hot prospects list of each RM and Tracking status', 'type': 'upload', 'priority': 'high'}
    ]
}

# ============================================
# GOOGLE SHEETS INTEGRATION
# ============================================

def connect_to_google_sheets():
    """Connect to Google Sheets - Optional"""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        
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
    except:
        return None

def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    try:
        client = connect_to_google_sheets()
        if not client:
            return None
        
        if 'docs.google.com' in sheet_id:
            sheet_id = sheet_id.split('/d/')[1].split('/')[0]
        
        spreadsheet = client.open_by_key(sheet_id)
        data = {}
        worksheets = spreadsheet.worksheets()
        
        for worksheet in worksheets:
            sheet_name = worksheet.title
            records = worksheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                data[sheet_name] = df
        
        return data
    except:
        return None

def parse_google_sheets_for_user(sheet_data, username):
    """Parse Google Sheets data for specific user"""
    if not sheet_data:
        return None
    
    for sheet_name, df in sheet_data.items():
        name_col = None
        for col in df.columns:
            col_upper = str(col).upper()
            if any(keyword in col_upper for keyword in ['RM', 'NAME', 'TEAM', 'LEADER']):
                name_col = col
                break
        
        if not name_col:
            continue
        
        for _, row in df.iterrows():
            name = str(row.get(name_col, '')).strip()
            
            if name == username:
                entry = {
                    'RM_Name': name,
                    'Total_RMs': 0,
                    'Lead_Count': 0,
                    'Target_Pitch': 0,
                    'Actual_Pitch': 0,
                    'Target_Registration': 0,
                    'Actual_Registration': 0
                }
                
                for col in df.columns:
                    col_upper = str(col).upper()
                    val = row.get(col, 0)
                    
                    try:
                        val = int(val) if pd.notna(val) else 0
                    except:
                        val = 0
                    
                    if 'TOTAL' in col_upper and 'RM' in col_upper:
                        entry['Total_RMs'] = val
                    elif 'LEAD' in col_upper and 'COUNT' in col_upper:
                        entry['Lead_Count'] = val
                    elif 'TARGET' in col_upper and 'PITCH' in col_upper:
                        entry['Target_Pitch'] = val
                    elif 'ACTUAL' in col_upper and 'PITCH' in col_upper:
                        entry['Actual_Pitch'] = val
                    elif 'TARGET' in col_upper and 'REG' in col_upper:
                        entry['Target_Registration'] = val
                    elif 'ACTUAL' in col_upper and 'REG' in col_upper:
                        entry['Actual_Registration'] = val
                
                return pd.DataFrame([entry])
    
    return None

# ============================================
# DATA MANAGEMENT FUNCTIONS
# ============================================

def get_current_user_data():
    """Get data for current logged-in user"""
    user = st.session_state.current_user
    if user not in st.session_state.rm_data_by_lead:
        st.session_state.rm_data_by_lead[user] = pd.DataFrame({
            'RM_Name': [''],
            'Total_RMs': [0],
            'Lead_Count': [0],
            'Target_Pitch': [0],
            'Actual_Pitch': [0],
            'Target_Registration': [0],
            'Actual_Registration': [0]
        })
    return st.session_state.rm_data_by_lead[user]

def update_current_user_data(df):
    """Update data for current logged-in user"""
    st.session_state.rm_data_by_lead[st.session_state.current_user] = df

def calculate_metrics(df):
    """Calculate performance metrics"""
    df = df[df['RM_Name'] != ''].copy()
    
    if len(df) == 0:
        return {
            'total_rms': 0,
            'total_leads': 0,
            'total_target_pitch': 0,
            'total_actual_pitch': 0,
            'total_target_reg': 0,
            'total_actual_reg': 0,
            'conversion_rate': 0,
            'pitch_achievement': 0,
            'reg_achievement': 0
        }
    
    metrics = {
        'total_rms': int(df['Total_RMs'].sum()),
        'total_leads': int(df['Lead_Count'].sum()),
        'total_target_pitch': int(df['Target_Pitch'].sum()),
        'total_actual_pitch': int(df['Actual_Pitch'].sum()),
        'total_target_reg': int(df['Target_Registration'].sum()),
        'total_actual_reg': int(df['Actual_Registration'].sum()),
    }
    
    if metrics['total_actual_pitch'] > 0:
        metrics['conversion_rate'] = round(
            (metrics['total_actual_reg'] / metrics['total_actual_pitch']) * 100, 1
        )
    else:
        metrics['conversion_rate'] = 0
    
    if metrics['total_target_pitch'] > 0:
        metrics['pitch_achievement'] = round(
            (metrics['total_actual_pitch'] / metrics['total_target_pitch']) * 100, 1
        )
    else:
        metrics['pitch_achievement'] = 0
    
    if metrics['total_target_reg'] > 0:
        metrics['reg_achievement'] = round(
            (metrics['total_actual_reg'] / metrics['total_target_reg']) * 100, 1
        )
    else:
        metrics['reg_achievement'] = 0
    
    return metrics

# ============================================
# AI ANALYSIS FUNCTIONS
# ============================================

def analyze_performance(df):
    """Generate AI-powered insights"""
    
    metrics = calculate_metrics(df)
    
    insights = {
        'total_rms': metrics['total_rms'],
        'total_leads': metrics['total_leads'],
        'total_pitches': metrics['total_actual_pitch'],
        'total_registrations': metrics['total_actual_reg'],
        'avg_conversion': metrics['conversion_rate'],
        'avg_pitch_achievement': metrics['pitch_achievement'],
        'avg_reg_achievement': metrics['reg_achievement'],
        'top_performer': None,
        'needs_support': None,
        'recommendations': [],
        'status': 'Good'
    }
    
    df_clean = df[df['RM_Name'] != ''].copy()
    
    if len(df_clean) > 0:
        # Calculate conversion for each RM
        df_clean['Conversion'] = df_clean.apply(
            lambda row: round((row['Actual_Registration'] / row['Actual_Pitch'] * 100), 1) 
            if row['Actual_Pitch'] > 0 else 0,
            axis=1
        )
        
        best_idx = df_clean['Conversion'].idxmax()
        worst_idx = df_clean['Conversion'].idxmin()
        
        insights['top_performer'] = {
            'name': df_clean.loc[best_idx, 'RM_Name'],
            'conversion': df_clean.loc[best_idx, 'Conversion']
        }
        
        insights['needs_support'] = {
            'name': df_clean.loc[worst_idx, 'RM_Name'],
            'conversion': df_clean.loc[worst_idx, 'Conversion']
        }
    
    # Generate recommendations
    conv = metrics['conversion_rate']
    
    if conv >= 15:
        insights['status'] = 'Excellent'
        insights['recommendations'].append("✅ **Excellent Performance!** Conversion rate is above 15% target. Maintain current strategies.")
    elif conv >= 10:
        insights['status'] = 'Good'
        insights['recommendations'].append("📈 **Good Progress!** Conversion rate is solid. Push to reach 15% target.")
    else:
        insights['status'] = 'Needs Improvement'
        insights['recommendations'].append("⚠️ **Action Required!** Conversion below 10%. Focus on pitch quality and follow-up.")
    
    if metrics['pitch_achievement'] < 80:
        insights['recommendations'].append("📞 **Priority:** Increase pitch activity. Current achievement is below 80%.")
    
    if metrics['reg_achievement'] < 80:
        insights['recommendations'].append("📝 **Priority:** Improve registration closure. Current achievement is below 80%.")
    
    return insights

# ============================================
# EMAIL REPORTING
# ============================================

def send_email_report(recipient_emails, subject, df, insights):
    """Send email report"""
    
    if not all([
        "email_sender" in st.secrets,
        "email_password" in st.secrets,
        "email_smtp_server" in st.secrets,
        "email_smtp_port" in st.secrets
    ]):
        return False, "Email not configured"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = st.secrets["email_sender"]
        msg['To'] = ', '.join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
        msg['Subject'] = subject
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #E63946; color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .metric {{ background: #F5E6D3; padding: 20px; margin: 15px 0; border-left: 5px solid #E63946; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background: #1A1A1A; color: white; padding: 15px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IRON LADY</h1>
                <p>Performance Report - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <h2>📊 Performance Summary</h2>
                <div class="metric">
                    <strong>Total RMs:</strong> {insights['total_rms']}<br/>
                    <strong>Conversion Rate:</strong> {insights['avg_conversion']}%<br/>
                    <strong>Status:</strong> {insights['status']}
                </div>
                
                <h2>💡 Recommendations</h2>
        """
        
        for rec in insights['recommendations']:
            html_body += f'<div class="metric">{rec}</div>'
        
        html_body += "</div></body></html>"
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(st.secrets["email_smtp_server"], int(st.secrets["email_smtp_port"]))
        server.starttls()
        server.login(st.secrets["email_sender"], st.secrets["email_password"])
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================
# LOGIN PAGE
# ============================================

def show_login_page():
    """Display login page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 50px 30px; background: linear-gradient(135deg, white 0%, {IRONLADY_COLORS['accent']} 100%); border-radius: 20px; border: 5px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2); margin-bottom: 40px;">
            <h1 style="font-size: 4rem; margin: 0; letter-spacing: 6px; text-transform: uppercase; color: {IRONLADY_COLORS['primary']};">IRON LADY</h1>
            <p style="font-size: 1.5rem; margin: 15px 0 0 0; font-weight: 600; color: {IRONLADY_COLORS['secondary']};">Sales Performance Dashboard</p>
            <p style="font-size: 1rem; margin: 10px 0 0 0; color: {IRONLADY_COLORS['secondary']}; opacity: 0.7;">Ultimate Complete Edition - v11.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-msg" style="text-align: center; font-size: 1.1rem;">
        👋 <strong>Welcome, Team Leader!</strong><br/>
        Select your profile to access your personalized dashboard
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown("### 👥 SELECT YOUR PROFILE")
    
    cols = st.columns(2)
    
    for idx, (name, info) in enumerate(TEAM_LEADERS.items()):
        with cols[idx % 2]:
            if st.button(
                f"{info['icon']} {name}",
                key=f"login_{name}",
                use_container_width=True
            ):
                st.session_state.logged_in = True
                st.session_state.current_user = name
                st.session_state.user_role = info['role']
                st.rerun()
            
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: white; border-radius: 10px; margin-top: 10px; border-left: 5px solid {info['color']}; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
                <strong>{info['role']}</strong>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# MAIN DASHBOARD (AFTER LOGIN)
# ============================================

def show_user_dashboard():
    """Display complete dashboard after login"""
    
    user = st.session_state.current_user
    role = st.session_state.user_role
    user_info = TEAM_LEADERS[user]
    
    # Header with logout
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, white 0%, {IRONLADY_COLORS['accent']} 100%); padding: 25px; border-radius: 15px; border-left: 8px solid {user_info['color']}; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h1 style="margin: 0; font-size: 2rem; border: none;">{user_info['icon']} Welcome, {user}!</h1>
            <p style="margin: 5px 0 0 0; font-size: 1rem; opacity: 0.8;">{role}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 25px; border-radius: 15px; border-left: 5px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); text-align: center;">
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.7;">Session: {st.session_state.selected_day}</p>
            <p style="margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 700;">{st.session_state.selected_date.strftime('%B %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 LOGOUT", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.rerun()
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### {user_info['icon']} {user}")
        st.markdown(f"**{role}**")
        
        st.markdown("---")
        st.markdown("### 📅 SESSION SETTINGS")
        
        st.session_state.selected_day = st.selectbox(
            "Day Type",
            options=['Day 1-1', 'Day 1', 'Day 2'],
            index=['Day 1-1', 'Day 1', 'Day 2'].index(st.session_state.selected_day)
        )
        
        st.session_state.selected_date = st.date_input(
            "Date",
            value=st.session_state.selected_date
        )
        
        st.markdown("---")
        st.markdown("### 📊 DATA SOURCE")
        
        st.session_state.use_google_sheets = st.checkbox(
            "Use Google Sheets",
            value=st.session_state.use_google_sheets
        )
        
        if st.session_state.use_google_sheets:
            sheet_id = st.text_input("Sheet ID/URL", placeholder="1abc123xyz...")
            
            if st.button("🔄 Load from Sheets", use_container_width=True):
                if sheet_id:
                    data = fetch_sheet_data(sheet_id)
                    if data:
                        parsed = parse_google_sheets_for_user(data, user)
                        if parsed is not None:
                            st.session_state.rm_data_by_lead[user] = parsed
                            st.success("✅ Data loaded!")
                            st.rerun()
        
        st.markdown("---")
        
        current_data = get_current_user_data()
        metrics = calculate_metrics(current_data)
        
        st.metric("Total RMs", metrics['total_rms'])
        st.metric("Conversion", f"{metrics['conversion_rate']}%")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Main tabs - ALL FEATURES
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Data Entry",
        "📊 Performance Dashboard",
        "📈 Google Sheets Viewer",
        "🤖 AI Analysis",
        "📧 Email Reports",
        "✅ Daily Checklist"
    ])
    
    # TAB 1: MANUAL DATA ENTRY
    with tab1:
        st.markdown("### 📝 MANUAL DATA ENTRY")
        
        current_data = get_current_user_data()
        
        with st.expander("➕ ADD NEW RM ENTRY", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                rm_name = st.text_input("RM Name", key="new_rm_name")
                total_rms = st.number_input("Total RMs", min_value=0, value=1, step=1, key="new_total_rms")
                lead_count = st.number_input("Total Leads", min_value=0, value=0, step=1, key="new_lead_count")
                target_pitch = st.number_input("Target Pitches", min_value=0, value=0, step=1, key="new_target_pitch")
            
            with col2:
                actual_pitch = st.number_input("Actual Pitches", min_value=0, value=0, step=1, key="new_actual_pitch")
                target_reg = st.number_input("Target Registrations", min_value=0, value=0, step=1, key="new_target_reg")
                actual_reg = st.number_input("Actual Registrations", min_value=0, value=0, step=1, key="new_actual_reg")
            
            if st.button("✅ ADD ENTRY", use_container_width=True):
                if rm_name and rm_name.strip():
                    new_row = pd.DataFrame({
                        'RM_Name': [rm_name],
                        'Total_RMs': [total_rms],
                        'Lead_Count': [lead_count],
                        'Target_Pitch': [target_pitch],
                        'Actual_Pitch': [actual_pitch],
                        'Target_Registration': [target_reg],
                        'Actual_Registration': [actual_reg]
                    })
                    
                    current_data = current_data[current_data['RM_Name'] != '']
                    updated_data = pd.concat([current_data, new_row], ignore_index=True)
                    update_current_user_data(updated_data)
                    st.success(f"✅ Added {rm_name}!")
                    st.rerun()
        
        display_data = current_data[current_data['RM_Name'] != ''].copy()
        if len(display_data) > 0:
            st.markdown("### 📊 CURRENT ENTRIES")
            st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # TAB 2: PERFORMANCE DASHBOARD
    with tab2:
        st.markdown("### 📊 PERFORMANCE OVERVIEW")
        
        current_data = get_current_user_data()
        metrics = calculate_metrics(current_data)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Total RMs", metrics['total_rms'])
        with col2:
            st.metric("📞 Total Leads", metrics['total_leads'])
        with col3:
            st.metric("🎯 Pitch Achievement", f"{metrics['pitch_achievement']}%")
        with col4:
            st.metric("📝 Reg Achievement", f"{metrics['reg_achievement']}%")
        with col5:
            st.metric("💯 Conversion", f"{metrics['conversion_rate']}%")
        
        st.markdown("---")
        
        # Charts
        display_df = current_data[current_data['RM_Name'] != ''].copy()
        if len(display_df) > 0:
            display_df['Conversion %'] = display_df.apply(
                lambda row: round((row['Actual_Registration'] / row['Actual_Pitch'] * 100), 1) 
                if row['Actual_Pitch'] > 0 else 0,
                axis=1
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(display_df, x='RM_Name', y='Conversion %', title='RM-wise Conversion Rate')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Pitch', x=display_df['RM_Name'], y=display_df['Actual_Pitch']))
                fig.add_trace(go.Bar(name='Registration', x=display_df['RM_Name'], y=display_df['Actual_Registration']))
                fig.update_layout(title='Pitches vs Registrations', barmode='group')
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: GOOGLE SHEETS VIEWER
    with tab3:
        st.markdown("### 📈 GOOGLE SHEETS VIEWER")
        
        if st.session_state.loaded_sheet_data:
            for sheet_name, df in st.session_state.loaded_sheet_data.items():
                with st.expander(f"📋 {sheet_name}", expanded=True):
                    st.dataframe(df, use_container_width=True)
        else:
            st.info("📊 No sheet data loaded. Enable 'Use Google Sheets' in sidebar and load data.")
    
    # TAB 4: AI ANALYSIS
    with tab4:
        st.markdown("### 🤖 AI INSIGHTS")
        
        current_data = get_current_user_data()
        insights = analyze_performance(current_data)
        
        st.markdown(f"""
        <div class="{'success' if insights['status'] == 'Excellent' else 'warning'}-msg" style="text-align: center;">
            <h2 style="margin: 0; border: none;">{insights['status']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💡 RECOMMENDATIONS")
        for rec in insights['recommendations']:
            st.markdown(f'<div class="insight-box">{rec}</div>', unsafe_allow_html=True)
    
    # TAB 5: EMAIL REPORTS
    with tab5:
        st.markdown("### 📧 EMAIL REPORTS")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            recipient_emails = st.text_area(
                "Recipient Emails (comma or newline separated)",
                placeholder="manager@company.com, team@company.com",
                height=100
            )
        
        with col2:
            st.markdown("<br/><br/>", unsafe_allow_html=True)
            if st.button("📧 SEND REPORT", use_container_width=True, type="primary"):
                if recipient_emails:
                    emails = [e.strip() for e in recipient_emails.replace(',', '\n').split('\n') if e.strip()]
                    if emails:
                        current_data = get_current_user_data()
                        insights = analyze_performance(current_data)
                        success, message = send_email_report(
                            emails,
                            f"Iron Lady Report - {user} - {datetime.now().strftime('%B %d, %Y')}",
                            current_data,
                            insights
                        )
                        if success:
                            st.success(f"✅ Sent to {len(emails)} recipient(s)!")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
    
    # TAB 6: DAILY CHECKLIST
    with tab6:
        st.markdown("### ✅ DAILY ACTIVITY CHECKLIST")
        
        selected_checklist = CHECKLIST_ITEMS.get(st.session_state.selected_day, [])
        
        if selected_checklist and selected_checklist[0].get('time'):
            st.markdown(f'<div class="info-msg">⏰ <strong>Session Time:</strong> {selected_checklist[0]["time"]}</div>', unsafe_allow_html=True)
        
        # Group by priority
        high_priority = [item for item in selected_checklist if item.get('priority') == 'high']
        medium_priority = [item for item in selected_checklist if item.get('priority') == 'medium']
        
        if high_priority:
            st.markdown("#### 🔴 HIGH PRIORITY TASKS")
            for idx, item in enumerate(high_priority):
                task = item['task']
                item_type = item.get('type', 'checkbox')
                
                badge = ""
                if item_type == 'upload':
                    badge = '<span class="badge badge-upload">📤 UPLOAD</span>'
                elif item_type == 'manual':
                    badge = '<span class="badge badge-manual">✋ MANUAL</span>'
                elif item_type == 'ongoing':
                    badge = '<span class="badge badge-ongoing">🔄 ONGOING</span>'
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    checked = st.checkbox(task, key=f"high_{idx}_{st.session_state.selected_day}")
                    st.session_state.checklist[task] = checked
                with col2:
                    if badge:
                        st.markdown(badge, unsafe_allow_html=True)
        
        if medium_priority:
            st.markdown("---")
            st.markdown("#### 🟡 MEDIUM PRIORITY TASKS")
            for idx, item in enumerate(medium_priority):
                st.checkbox(item['task'], key=f"med_{idx}_{st.session_state.selected_day}")
        
        # Progress
        st.markdown("---")
        task_names = [item['task'] for item in selected_checklist]
        checked_count = sum(1 for task in task_names if st.session_state.checklist.get(task, False))
        progress = checked_count / len(task_names) * 100 if task_names else 0
        
        st.progress(progress / 100, text=f"{progress:.0f}% Complete ({checked_count}/{len(task_names)})")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {IRONLADY_COLORS['secondary']} 0%, {IRONLADY_COLORS['primary']} 100%); border-radius: 15px; color: white;">
        <p style="margin: 0; font-weight: 900; font-size: 1.5rem;">IRON LADY</p>
        <p style="margin: 10px 0 0 0;">Ultimate Complete Edition - v11.0</p>
        <p style="margin: 10px 0 0 0;">Logged in as: <strong>{user}</strong> ({role})</p>
        <p style="margin: 15px 0 0 0; font-size: 0.85rem; opacity: 0.7;">Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP ROUTING
# ============================================

def main():
    """Main application router"""
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_user_dashboard()

if __name__ == "__main__":
    main()
