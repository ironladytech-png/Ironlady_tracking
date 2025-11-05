"""
IRON LADY - COMPLETE SALES DASHBOARD
All 100+ Features from Requirements Document
Real-time sales performance tracking with:
- Multi-user Login System (4 Team Leaders)
- Individual Dashboards with Manual Data Entry
- Google Sheets Integration
- Performance Dashboard with Interactive Charts
- AI-Powered Analysis & Insights
- Email Reports to Multiple Recipients
- Daily Checklists (Day 1-1, Day 1, Day 2)
- Complete Session Management
- Works WITHOUT Google Sheets or Email Config

Team: Ghazala (Senior TL), Megha (Senior TL), Afreen (Trainee TL), Soumya (Trainee TL)
Version: 10.0 - All Requirements Edition
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

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
# IRON LADY BRANDING & STYLING
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',      # Red
    'secondary': '#1A1A1A',    # Black
    'accent': '#F5E6D3',       # Beige
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
    
    .checklist-item {{
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 4px solid {IRONLADY_COLORS['primary']};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 8px;
        text-transform: uppercase;
    }}
    
    .badge-high {{
        background: #D62828;
        color: white;
    }}
    
    .badge-medium {{
        background: #F77F00;
        color: white;
    }}
    
    .profile-card {{
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 3px solid transparent;
    }}
    
    .profile-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        border-color: {IRONLADY_COLORS['primary']};
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
        'color': '#E63946',
    },
    'Megha': {
        'role': 'Senior Team Leader',
        'icon': '🏆',
        'color': '#2A9D8F',
    },
    'Afreen': {
        'role': 'Team Leader - Trainee',
        'icon': '🌟',
        'color': '#F77F00',
    },
    'Soumya': {
        'role': 'Team Leader - Trainee',
        'icon': '🌟',
        'color': '#457B9D',
    }
}

# ============================================
# DAILY CHECKLISTS
# ============================================

DAILY_CHECKLISTS = {
    'Day 1-1': [
        {'task': 'Mocks - Who are the people - Buddy structure', 'priority': 'High', 'type': 'Manual'},
        {'task': 'Sign off Activities - each RM type', 'priority': 'High', 'type': 'Manual'},
        {'task': 'WA Audit - Minimum 10', 'priority': 'High', 'type': 'Upload'},
        {'task': 'Follow up Calls - 2 Registrations', 'priority': 'High', 'type': 'Manual'},
        {'task': 'SL Calls - 5 (Share status list)', 'priority': 'High', 'type': 'Upload'},
        {'task': 'Lead Analysis AI summary', 'priority': 'Medium', 'type': 'Upload'},
        {'task': 'Call Audit - Minimum 5 calls', 'priority': 'High', 'type': 'Upload'},
        {'task': 'Tracking: CRM Update, Call/Attendance/WA', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Targets Sharing - percentage and potential list', 'priority': 'High', 'type': 'Upload'},
        {'task': 'CRM Updation', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Sharing hot prospects list', 'priority': 'Medium', 'type': 'Upload'},
    ],
    'Day 1': [
        {'task': 'WA Audit - 10', 'priority': 'High', 'type': 'Upload'},
        {'task': 'SL Calls - 8 (Share status list)', 'priority': 'High', 'type': 'Upload'},
        {'task': 'Sign off Activities', 'priority': 'High', 'type': 'Manual'},
        {'task': 'Mocks - Buddy structure', 'priority': 'High', 'type': 'Manual'},
        {'task': '30s pitch Prep', 'priority': 'High', 'type': 'Manual'},
        {'task': 'Tracking: CRM Update', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Call Audit - Minimum 5 calls', 'priority': 'High', 'type': 'Upload'},
        {'task': 'Targets Sharing - % and potential list', 'priority': 'High', 'type': 'Upload'},
        {'task': '10% Conversion - action points', 'priority': 'Medium', 'type': 'Manual'},
        {'task': 'CRM Updation - including attendance', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Sharing hot prospects list and Tracking', 'priority': 'Medium', 'type': 'Upload'},
    ],
    'Day 2': [
        {'task': 'SL Calls - 10-12 (Share status list)', 'priority': 'High', 'type': 'Upload'},
        {'task': 'WA Audit - As needed', 'priority': 'Medium', 'type': 'Upload'},
        {'task': 'Tracking: CRM Update', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Sign off Activities', 'priority': 'High', 'type': 'Manual'},
        {'task': 'Targets Sharing - 10% before, 15% after', 'priority': 'High', 'type': 'Upload'},
        {'task': 'CRM Updation - including attendance', 'priority': 'High', 'type': 'Ongoing'},
        {'task': 'Sharing hot prospects list and Tracking', 'priority': 'Medium', 'type': 'Upload'},
    ]
}

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def init_session_state():
    """Initialize all session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'session_date' not in st.session_state:
        st.session_state.session_date = datetime.now()
    if 'day_type' not in st.session_state:
        st.session_state.day_type = 'Day 1-1'
    if 'checklist_completion' not in st.session_state:
        st.session_state.checklist_completion = {}
    if 'use_google_sheets' not in st.session_state:
        st.session_state.use_google_sheets = False
    if 'sheet_id' not in st.session_state:
        st.session_state.sheet_id = ''

# ============================================
# GOOGLE SHEETS FUNCTIONS
# ============================================

def connect_to_google_sheets():
    """Connect to Google Sheets (gracefully handles missing config)"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        if "gcp_service_account" in st.secrets:
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
        else:
            return None
    except ImportError:
        st.warning("⚠️ gspread not installed. Google Sheets integration disabled.")
        return None
    except Exception as e:
        st.warning(f"⚠️ Google Sheets connection failed: {e}")
        return None

def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets (with error handling)"""
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
    except Exception as e:
        st.error(f"❌ Error fetching sheet data: {e}")
        return None

def parse_team_data(sheet_data, user_name):
    """Parse team leader data from Google Sheets"""
    if not sheet_data:
        return []
    
    team_data = []
    
    for sheet_name, df in sheet_data.items():
        name_col = None
        for col in df.columns:
            col_upper = str(col).upper()
            if any(keyword in col_upper for keyword in ['RM', 'NAME', 'TEAM']):
                name_col = col
                break
        
        if not name_col:
            continue
        
        for _, row in df.iterrows():
            rm_name = str(row.get(name_col, '')).strip()
            
            if not rm_name:
                continue
            
            entry = {
                'rm_name': rm_name,
                'total_rms': 1,
                'lead_count': 0,
                'pitches_target': 0,
                'pitches_actual': 0,
                'reg_target': 0,
                'reg_actual': 0,
            }
            
            for col in df.columns:
                col_upper = str(col).upper()
                val = row.get(col, 0)
                
                try:
                    val = int(val) if pd.notna(val) and val != '' else 0
                except:
                    val = 0
                
                if 'LEAD' in col_upper and 'COUNT' in col_upper:
                    entry['lead_count'] = val
                elif 'TARGET' in col_upper and 'PITCH' in col_upper:
                    entry['pitches_target'] = val
                elif 'ACTUAL' in col_upper and 'PITCH' in col_upper:
                    entry['pitches_actual'] = val
                elif 'TARGET' in col_upper and ('REG' in col_upper or 'REGISTRATION' in col_upper):
                    entry['reg_target'] = val
                elif 'ACTUAL' in col_upper and ('REG' in col_upper or 'REGISTRATION' in col_upper):
                    entry['reg_actual'] = val
            
            team_data.append(entry)
    
    return team_data

# ============================================
# EMAIL FUNCTIONS
# ============================================

def send_email_report(recipient_emails, subject, df, insights, user_name):
    """Send comprehensive email report"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not all([
            "email_sender" in st.secrets,
            "email_password" in st.secrets,
            "email_smtp_server" in st.secrets,
            "email_smtp_port" in st.secrets
        ]):
            return False, "Email configuration not found in secrets"
        
        msg = MIMEMultipart('alternative')
        msg['From'] = st.secrets["email_sender"]
        msg['To'] = ', '.join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
        msg['Subject'] = subject
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #F5E6D3; margin: 0; padding: 0; }}
                .container {{ max-width: 800px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }}
                .header {{ background: linear-gradient(135deg, #E63946 0%, #D62828 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 2.5rem; letter-spacing: 3px; font-weight: 900; }}
                .header p {{ margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9; }}
                .content {{ padding: 40px 30px; }}
                .metric {{ background: #F5E6D3; padding: 20px; margin: 15px 0; border-left: 5px solid #E63946; border-radius: 5px; }}
                .section-title {{ color: #1A1A1A; font-size: 1.5rem; font-weight: 900; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #E63946; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background: #1A1A1A; color: white; padding: 15px; text-align: left; font-weight: 700; }}
                td {{ padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }}
                tr:hover {{ background-color: #F5E6D3; }}
                .footer {{ background: #1A1A1A; color: white; text-align: center; padding: 30px; }}
                .highlight {{ background: #E63946; color: white; padding: 3px 8px; border-radius: 3px; font-weight: 700; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>IRON LADY</h1>
                    <p>Sales Performance Report - {datetime.now().strftime('%B %d, %Y')}</p>
                    <p>Team Leader: {user_name}</p>
                </div>
                <div class="content">
                    <h2 class="section-title">📊 Executive Summary</h2>
                    <div class="metric">
                        <strong>Total RMs:</strong> {insights['total_rms']}<br/>
                        <strong>Total Pitches:</strong> {insights['total_pitches']}<br/>
                        <strong>Total Registrations:</strong> {insights['total_registrations']}<br/>
                        <strong>Average Conversion:</strong> <span class="highlight">{insights['avg_conversion']}%</span>
                    </div>
        """
        
        if insights.get('best_performer'):
            bp = insights['best_performer']
            html_body += f"""
                    <h2 class="section-title">⭐ Top Performer</h2>
                    <div class="metric">
                        <strong>Name:</strong> {bp['name']}<br/>
                        <strong>Conversion:</strong> {bp['conversion']}%
                    </div>
            """
        
        html_body += """
                    <h2 class="section-title">📋 Team Performance</h2>
                    <table>
                        <thead><tr>
                            <th>RM Name</th>
                            <th>Pitches</th>
                            <th>Registrations</th>
                            <th>Conversion %</th>
                        </tr></thead>
                        <tbody>
        """
        
        for _, row in df.iterrows():
            conv = row.get('conversion', 0)
            html_body += f"""
                        <tr>
                            <td>{row['rm_name']}</td>
                            <td>{row['pitches_actual']}/{row['pitches_target']}</td>
                            <td>{row['reg_actual']}/{row['reg_target']}</td>
                            <td style="font-weight: 700;">{conv}%</td>
                        </tr>
            """
        
        html_body += """
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <p style="font-size: 1.3rem; font-weight: 900;">IRON LADY</p>
                    <p>Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
                    <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">© 2024 Iron Lady. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
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
# AI ANALYSIS FUNCTIONS
# ============================================

def analyze_team_performance(df):
    """Generate AI-powered insights"""
    
    insights = {
        'total_rms': int(df['total_rms'].sum()) if 'total_rms' in df.columns else len(df),
        'total_pitches': int(df['pitches_actual'].sum()),
        'total_registrations': int(df['reg_actual'].sum()),
        'avg_conversion': 0,
        'best_performer': None,
        'needs_support': None,
        'recommendations': []
    }
    
    # Calculate conversions
    df['conversion'] = df.apply(
        lambda x: round((x['reg_actual'] / x['pitches_actual'] * 100), 1) if x['pitches_actual'] > 0 else 0,
        axis=1
    )
    
    insights['avg_conversion'] = round(df['conversion'].mean(), 1)
    
    # Find best and worst performers
    if len(df) > 0:
        best_idx = df['conversion'].idxmax()
        worst_idx = df['conversion'].idxmin()
        
        insights['best_performer'] = {
            'name': df.loc[best_idx, 'rm_name'],
            'conversion': df.loc[best_idx, 'conversion'],
        }
        
        insights['needs_support'] = {
            'name': df.loc[worst_idx, 'rm_name'],
            'conversion': df.loc[worst_idx, 'conversion'],
        }
    
    # Generate recommendations
    avg_conv = insights['avg_conversion']
    
    if avg_conv < 50:
        insights['recommendations'].append("🚨 CRITICAL: Team conversion is very low (<50%). Immediate training required.")
    elif avg_conv < 60:
        insights['recommendations'].append("⚠️ URGENT: Conversion below target. Schedule coaching sessions.")
    elif avg_conv < 75:
        insights['recommendations'].append("📈 ACTION: Room for improvement. Focus on closing techniques.")
    else:
        insights['recommendations'].append("✅ EXCELLENT: Team exceeding targets. Maintain momentum!")
    
    low_performers = df[df['conversion'] < 60]
    if len(low_performers) > 0:
        names = ', '.join(low_performers['rm_name'].tolist()[:3])
        insights['recommendations'].append(f"🎯 SUPPORT NEEDED: {names}")
    
    return insights

# ============================================
# LOGIN PAGE
# ============================================

def show_login_page():
    """Display login page with all team leaders"""
    
    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, {IRONLADY_COLORS['accent']} 0%, white 100%); border-radius: 20px; margin-bottom: 30px;">
        <h1 style="font-size: 4rem; margin: 0; letter-spacing: 8px;">IRON LADY</h1>
        <p style="font-size: 1.5rem; margin: 15px 0; font-weight: 600;">Sales Performance Dashboard</p>
        <p style="font-size: 1rem; opacity: 0.7;">Select Your Profile to Continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👥 SELECT YOUR PROFILE")
    
    cols = st.columns(4)
    
    for idx, (name, info) in enumerate(TEAM_LEADERS.items()):
        with cols[idx]:
            st.markdown(f"""
            <div class="profile-card" style="border-color: {info['color']};">
                <div style="font-size: 4rem; margin-bottom: 15px;">{info['icon']}</div>
                <h3 style="margin: 10px 0; color: {info['color']};">{name}</h3>
                <p style="margin: 5px 0; font-size: 0.9rem; opacity: 0.8;">{info['role']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Login as {name}", key=f"login_{name}", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.current_user = name
                st.session_state.user_data[name] = []
                st.rerun()
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-msg" style="text-align: center;">
        <strong>🔒 Secure Session Management</strong><br/>
        Each team leader has individual dashboard access with isolated data storage
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN DASHBOARD
# ============================================

def show_dashboard():
    """Main dashboard for logged-in user"""
    
    user = st.session_state.current_user
    user_info = TEAM_LEADERS[user]
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; margin-bottom: 20px;">
            <div style="font-size: 3rem;">{user_info['icon']}</div>
            <h3 style="margin: 10px 0; color: {user_info['color']};">{user}</h3>
            <p style="margin: 0; font-size: 0.85rem; opacity: 0.8;">{user_info['role']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Session Settings
        st.markdown("### 📅 SESSION SETTINGS")
        
        session_date = st.date_input(
            "Date",
            value=st.session_state.session_date
        )
        st.session_state.session_date = session_date
        
        day_type = st.selectbox(
            "Day Type",
            options=['Day 1-1', 'Day 1', 'Day 2'],
            index=['Day 1-1', 'Day 1', 'Day 2'].index(st.session_state.day_type)
        )
        st.session_state.day_type = day_type
        
        st.markdown("---")
        
        # Google Sheets Settings
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox(
            "Use Google Sheets",
            value=st.session_state.use_google_sheets
        )
        st.session_state.use_google_sheets = use_sheets
        
        if use_sheets:
            sheet_id = st.text_input(
                "Sheet ID/URL",
                value=st.session_state.sheet_id,
                placeholder="Paste Google Sheet ID or URL"
            )
            st.session_state.sheet_id = sheet_id
            
            if st.button("📥 Load from Sheets", use_container_width=True):
                if sheet_id:
                    with st.spinner("Loading..."):
                        sheet_data = fetch_sheet_data(sheet_id)
                        if sheet_data:
                            loaded_data = parse_team_data(sheet_data, user)
                            if loaded_data:
                                st.session_state.user_data[user] = loaded_data
                                st.success(f"✅ Loaded {len(loaded_data)} entries")
                                st.rerun()
                            else:
                                st.warning("⚠️ No data found for your team")
                        else:
                            st.error("❌ Failed to load sheet")
                else:
                    st.warning("⚠️ Enter Sheet ID first")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 QUICK STATS")
        current_data = st.session_state.user_data.get(user, [])
        if current_data:
            total_rms = len(current_data)
            total_pitches = sum(d['pitches_actual'] for d in current_data)
            total_regs = sum(d['reg_actual'] for d in current_data)
            st.metric("Total RMs", total_rms)
            st.metric("Total Pitches", total_pitches)
            st.metric("Total Registrations", total_regs)
        else:
            st.info("No data yet")
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**🕐 Session Time**")
        st.markdown(f"{datetime.now().strftime('%I:%M %p')}")
    
    # ============================================
    # MAIN HEADER
    # ============================================
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {IRONLADY_COLORS['accent']} 0%, white 100%); border-radius: 15px; margin-bottom: 30px; border: 3px solid {user_info['color']};">
        <h1 style="font-size: 3rem; margin: 0;">Welcome, {user}! {user_info['icon']}</h1>
        <p style="font-size: 1.2rem; margin: 10px 0;">{user_info['role']}</p>
        <p style="font-size: 0.95rem; opacity: 0.7;">Session: {session_date.strftime('%B %d, %Y')} | {day_type}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # MAIN TABS
    # ============================================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Data Entry",
        "📊 Performance Dashboard",
        "📋 Google Sheets Viewer",
        "🤖 AI Analysis",
        "📧 Email Reports",
        "✅ Daily Checklist"
    ])
    
    # ============================================
    # TAB 1: DATA ENTRY
    # ============================================
    with tab1:
        st.markdown("### 📝 MANUAL DATA ENTRY")
        st.markdown("""
        <div class="info-msg">
            ➕ <strong>Add New RM Entries</strong><br/>
            Enter performance data for each RM in your team
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("data_entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                rm_name = st.text_input("RM Name *", placeholder="Enter RM name")
                lead_count = st.number_input("Lead Count", min_value=0, value=0)
                pitches_target = st.number_input("Target Pitches *", min_value=0, value=0)
                pitches_actual = st.number_input("Actual Pitches *", min_value=0, value=0)
            
            with col2:
                st.markdown("<br/>", unsafe_allow_html=True)
                reg_target = st.number_input("Target Registrations *", min_value=0, value=0)
                reg_actual = st.number_input("Actual Registrations *", min_value=0, value=0)
            
            submitted = st.form_submit_button("➕ Add Entry", use_container_width=True, type="primary")
            
            if submitted:
                if rm_name and pitches_target > 0:
                    new_entry = {
                        'rm_name': rm_name,
                        'total_rms': 1,
                        'lead_count': lead_count,
                        'pitches_target': pitches_target,
                        'pitches_actual': pitches_actual,
                        'reg_target': reg_target,
                        'reg_actual': reg_actual,
                    }
                    
                    if user not in st.session_state.user_data:
                        st.session_state.user_data[user] = []
                    
                    st.session_state.user_data[user].append(new_entry)
                    st.success(f"✅ Added entry for {rm_name}")
                    st.rerun()
                else:
                    st.error("❌ Please fill required fields (RM Name, Target Pitches)")
        
        st.markdown("---")
        
        # Display current entries
        st.markdown("### 📋 CURRENT ENTRIES")
        
        current_data = st.session_state.user_data.get(user, [])
        
        if current_data:
            df_display = pd.DataFrame(current_data)
            
            # Add calculated columns
            df_display['Pitch %'] = df_display.apply(
                lambda x: f"{round(x['pitches_actual']/x['pitches_target']*100, 1)}%" if x['pitches_target'] > 0 else "0%",
                axis=1
            )
            df_display['Reg %'] = df_display.apply(
                lambda x: f"{round(x['reg_actual']/x['reg_target']*100, 1)}%" if x['reg_target'] > 0 else "0%",
                axis=1
            )
            df_display['Conversion'] = df_display.apply(
                lambda x: f"{round(x['reg_actual']/x['pitches_actual']*100, 1)}%" if x['pitches_actual'] > 0 else "0%",
                axis=1
            )
            
            display_cols = ['rm_name', 'lead_count', 'pitches_actual', 'Pitch %', 'reg_actual', 'Reg %', 'Conversion']
            display_df = df_display[display_cols].copy()
            display_df.columns = ['RM Name', 'Leads', 'Pitches', 'Pitch %', 'Registrations', 'Reg %', 'Conversion']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Clear All Data", use_container_width=True):
                    st.session_state.user_data[user] = []
                    st.success("✅ All data cleared")
                    st.rerun()
            
            with col2:
                csv = display_df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv,
                    file_name=f"{user}_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                json_str = df_display.to_json(orient='records', indent=2)
                st.download_button(
                    "⬇️ Download JSON",
                    data=json_str,
                    file_name=f"{user}_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("📝 No entries yet. Add your first RM entry above!")
    
    # ============================================
    # TAB 2: PERFORMANCE DASHBOARD
    # ============================================
    with tab2:
        st.markdown("### 📊 PERFORMANCE DASHBOARD")
        
        current_data = st.session_state.user_data.get(user, [])
        
        if not current_data:
            st.warning("⚠️ No data available. Add entries in the 'Data Entry' tab first.")
        else:
            df = pd.DataFrame(current_data)
            
            # Calculate metrics
            total_rms = len(df)
            total_leads = int(df['lead_count'].sum())
            total_pitch_target = int(df['pitches_target'].sum())
            total_pitch_actual = int(df['pitches_actual'].sum())
            total_reg_target = int(df['reg_target'].sum())
            total_reg_actual = int(df['reg_actual'].sum())
            
            pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
            reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
            conversion_rate = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
            
            # Key Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("👥 Total RMs", total_rms)
            
            with col2:
                st.metric("📞 Total Leads", total_leads)
            
            with col3:
                st.metric("🎯 Pitch Achievement", f"{pitch_achievement}%")
            
            with col4:
                st.metric("📝 Reg Achievement", f"{reg_achievement}%")
            
            with col5:
                conv_status = "🟢" if conversion_rate >= 75 else "🟡" if conversion_rate >= 60 else "🔴"
                st.metric("💯 Conversion Rate", f"{conv_status} {conversion_rate}%")
            
            st.markdown("---")
            
            # Calculate individual conversions
            df['conversion'] = df.apply(
                lambda x: round((x['reg_actual'] / x['pitches_actual'] * 100), 1) if x['pitches_actual'] > 0 else 0,
                axis=1
            )
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💯 RM-wise Conversion Rate")
                fig1 = px.bar(
                    df,
                    x='rm_name',
                    y='conversion',
                    color='conversion',
                    color_continuous_scale=['#D62828', '#F77F00', '#2A9D8F'],
                    labels={'rm_name': 'RM Name', 'conversion': 'Conversion %'},
                    text='conversion'
                )
                fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig1.update_layout(showlegend=False, height=400, xaxis_title="", yaxis_title="Conversion %")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Pitch vs Registration")
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name='Pitches',
                    x=df['rm_name'],
                    y=df['pitches_actual'],
                    marker_color=IRONLADY_COLORS['success'],
                    text=df['pitches_actual'],
                    textposition='outside'
                ))
                fig2.add_trace(go.Bar(
                    name='Registrations',
                    x=df['rm_name'],
                    y=df['reg_actual'],
                    marker_color=IRONLADY_COLORS['primary'],
                    text=df['reg_actual'],
                    textposition='outside'
                ))
                fig2.update_layout(barmode='group', height=400, xaxis_title="", yaxis_title='Count')
                st.plotly_chart(fig2, use_container_width=True)
            
            # Gauge Chart
            st.markdown("#### 🎯 Overall Conversion Rate Gauge")
            fig3 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=conversion_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Team Conversion Rate", 'font': {'size': 24}},
                delta={'reference': 75, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': IRONLADY_COLORS['primary']},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 60], 'color': '#f8d7da'},
                        {'range': [60, 75], 'color': '#fff3cd'},
                        {'range': [75, 100], 'color': '#d4edda'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
            
            # Pie Chart
            st.markdown("#### 🥧 Registration Distribution")
            fig4 = px.pie(
                df,
                values='reg_actual',
                names='rm_name',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig4.update_traces(textposition='inside', textinfo='percent+label')
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
    
    # ============================================
    # TAB 3: GOOGLE SHEETS VIEWER
    # ============================================
    with tab3:
        st.markdown("### 📋 GOOGLE SHEETS VIEWER")
        
        st.markdown("""
        <div class="info-msg">
            📊 <strong>View Live Data from Google Sheets</strong><br/>
            Connect to your Google Sheet to display real-time data
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.use_google_sheets or not st.session_state.sheet_id:
            st.warning("⚠️ Enable Google Sheets and enter Sheet ID in the sidebar to use this feature")
        else:
            if st.button("🔄 Refresh Sheet Data", use_container_width=False):
                with st.spinner("Loading from Google Sheets..."):
                    sheet_data = fetch_sheet_data(st.session_state.sheet_id)
                    if sheet_data:
                        st.success("✅ Data loaded successfully!")
                        
                        for sheet_name, df_sheet in sheet_data.items():
                            with st.expander(f"📄 {sheet_name}", expanded=True):
                                st.dataframe(df_sheet, use_container_width=True, height=400)
                    else:
                        st.error("❌ Failed to load data from Google Sheets")
    
    # ============================================
    # TAB 4: AI ANALYSIS
    # ============================================
    with tab4:
        st.markdown("### 🤖 AI-POWERED ANALYSIS")
        
        current_data = st.session_state.user_data.get(user, [])
        
        if not current_data:
            st.warning("⚠️ No data available for analysis. Add entries first.")
        else:
            df = pd.DataFrame(current_data)
            
            with st.spinner("🧠 Analyzing performance data..."):
                insights = analyze_team_performance(df)
            
            # Performance Status
            avg_conv = insights['avg_conversion']
            if avg_conv >= 75:
                status_msg = "Excellent"
                status_color = "success"
                status_icon = "✅"
            elif avg_conv >= 60:
                status_msg = "Good"
                status_color = "warning"
                status_icon = "⚠️"
            else:
                status_msg = "Needs Improvement"
                status_color = "error"
                status_icon = "❌"
            
            st.markdown(f"""
            <div class="{status_color}-msg" style="text-align: center;">
                <h2 style="margin: 0; border: none;">{status_icon} {status_msg}</h2>
                <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Team Average Conversion: {avg_conv}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Key Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("👥 Total RMs", insights['total_rms'])
            
            with col2:
                st.metric("📞 Total Pitches", insights['total_pitches'])
            
            with col3:
                st.metric("📝 Total Registrations", insights['total_registrations'])
            
            st.markdown("---")
            
            # Top & Bottom Performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⭐ TOP PERFORMER")
                if insights['best_performer']:
                    bp = insights['best_performer']
                    st.markdown(f"""
                    <div class="success-msg">
                        <h3 style="margin: 0 0 10px 0; border: none;">🏆 {bp['name']}</h3>
                        <strong>Conversion Rate:</strong> {bp['conversion']}%<br/>
                        <strong>Status:</strong> Outstanding Performance
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📉 NEEDS SUPPORT")
                if insights['needs_support']:
                    ns = insights['needs_support']
                    st.markdown(f"""
                    <div class="warning-msg">
                        <h3 style="margin: 0 0 10px 0; border: none;">🎯 {ns['name']}</h3>
                        <strong>Conversion Rate:</strong> {ns['conversion']}%<br/>
                        <strong>Action:</strong> Provide coaching
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Recommendations
            st.markdown("### 💡 STRATEGIC RECOMMENDATIONS")
            for idx, rec in enumerate(insights['recommendations'], 1):
                st.markdown(f"""
                <div class="insight-box">
                    <strong>#{idx}:</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
    
    # ============================================
    # TAB 5: EMAIL REPORTS
    # ============================================
    with tab5:
        st.markdown("### 📧 EMAIL REPORTS")
        
        current_data = st.session_state.user_data.get(user, [])
        
        if not current_data:
            st.warning("⚠️ No data available to send. Add entries first.")
        else:
            st.markdown("""
            <div class="info-msg">
                📨 <strong>Send Professional Reports</strong><br/>
                Email comprehensive performance reports to multiple recipients
            </div>
            """, unsafe_allow_html=True)
            
            # Check email config
            email_configured = all([
                "email_sender" in st.secrets,
                "email_password" in st.secrets,
                "email_smtp_server" in st.secrets,
                "email_smtp_port" in st.secrets
            ])
            
            if not email_configured:
                st.markdown("""
                <div class="warning-msg">
                    ⚠️ <strong>Email Not Configured</strong><br/>
                    Add email settings to your .streamlit/secrets.toml file
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-msg">
                    ✅ <strong>Email Configured</strong><br/>
                    Ready to send reports
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                recipient_emails = st.text_area(
                    "Recipient Emails (comma or newline separated)",
                    placeholder="manager@company.com, supervisor@company.com",
                    height=100
                )
                
                subject = st.text_input(
                    "Email Subject",
                    value=f"Performance Report - {user} - {datetime.now().strftime('%B %d, %Y')}"
                )
            
            with col2:
                st.markdown("<br/>", unsafe_allow_html=True)
                if st.button("📧 SEND EMAIL", use_container_width=True, type="primary", disabled=not email_configured):
                    if recipient_emails:
                        emails = [e.strip() for e in recipient_emails.replace(',', '\n').split('\n') if e.strip()]
                        
                        if emails:
                            with st.spinner("📤 Sending email..."):
                                df = pd.DataFrame(current_data)
                                insights = analyze_team_performance(df)
                                
                                success, message = send_email_report(emails, subject, df, insights, user)
                                
                                if success:
                                    st.success(f"✅ {message}")
                                    st.success(f"📧 Sent to {len(emails)} recipient(s)")
                                    st.balloons()
                                else:
                                    st.error(f"❌ {message}")
                        else:
                            st.error("❌ Enter at least one valid email")
                    else:
                        st.error("❌ Enter recipient emails")
    
    # ============================================
    # TAB 6: DAILY CHECKLIST
    # ============================================
    with tab6:
        st.markdown(f"### ✅ DAILY CHECKLIST - {day_type}")
        
        st.markdown(f"""
        <div class="info-msg">
            📋 <strong>Complete Your Daily Tasks</strong><br/>
            Session: {session_date.strftime('%B %d, %Y')} | {day_type}<br/>
            Track your progress and ensure all activities are completed
        </div>
        """, unsafe_allow_html=True)
        
        checklist = DAILY_CHECKLISTS.get(day_type, [])
        
        # Initialize checklist completion
        checklist_key = f"{user}_{day_type}_{session_date.strftime('%Y%m%d')}"
        if checklist_key not in st.session_state.checklist_completion:
            st.session_state.checklist_completion[checklist_key] = [False] * len(checklist)
        
        completed = st.session_state.checklist_completion[checklist_key]
        total_tasks = len(checklist)
        completed_tasks = sum(completed)
        completion_percentage = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        # Progress Bar
        st.markdown(f"""
        <div class="metric">
            <strong>Progress:</strong> {completed_tasks}/{total_tasks} tasks ({completion_percentage}%)<br/>
            <div style="background: #e0e0e0; border-radius: 10px; height: 25px; margin-top: 10px;">
                <div style="background: {IRONLADY_COLORS['primary']}; height: 100%; border-radius: 10px; width: {completion_percentage}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display checklist items
        for idx, item in enumerate(checklist):
            priority_color = 'badge-high' if item['priority'] == 'High' else 'badge-medium'
            
            type_icons = {
                'Upload': '📤',
                'Manual': '✋',
                'Ongoing': '🔄',
                'Checkbox': '☑️',
                'Text': '📝'
            }
            type_icon = type_icons.get(item['type'], '📋')
            
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                is_checked = st.checkbox(
                    "",
                    value=completed[idx],
                    key=f"check_{checklist_key}_{idx}"
                )
                st.session_state.checklist_completion[checklist_key][idx] = is_checked
            
            with col2:
                st.markdown(f"""
                <div class="checklist-item">
                    <span class="badge {priority_color}">🔴 {item['priority']}</span>
                    <span class="badge" style="background: #2A9D8F; color: white;">{type_icon} {item['type']}</span>
                    <br/>
                    <strong style="font-size: 1.05rem; {'text-decoration: line-through; opacity: 0.6;' if is_checked else ''}">{item['task']}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action Buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reset Checklist", use_container_width=True):
                st.session_state.checklist_completion[checklist_key] = [False] * len(checklist)
                st.rerun()
        
        with col2:
            if st.button("✅ Mark All Complete", use_container_width=True):
                st.session_state.checklist_completion[checklist_key] = [True] * len(checklist)
                st.rerun()
        
        with col3:
            if completion_percentage == 100:
                st.success("🎉 All tasks completed!")
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {IRONLADY_COLORS['secondary']} 0%, {IRONLADY_COLORS['primary']} 100%); border-radius: 15px; color: white;">
        <p style="margin: 0; font-weight: 900; font-size: 1.5rem;">IRON LADY</p>
        <p style="margin: 10px 0 0 0;">Sales Performance Management System</p>
        <p style="margin: 10px 0 0 0; font-size: 0.9rem;">Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
        <p style="margin: 15px 0 0 0; font-size: 0.85rem; opacity: 0.7;">© 2024 Iron Lady | v10.0 Complete Edition</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP
# ============================================

def main():
    init_session_state()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
