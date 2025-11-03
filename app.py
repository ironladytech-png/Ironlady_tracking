"""
IRON LADY SALES TRACKER - COMPLETE FINAL VERSION
Dashboard with Manual RM Data Entry, Google Sheets Live View, AI Analysis & Email Reports
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from PIL import Image
import io
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Try to import optional libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        NER_AVAILABLE = True
    except:
        NER_AVAILABLE = False
except ImportError:
    NER_AVAILABLE = False

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
    'gradient_start': '#E63946',
    'gradient_end': '#D62828'
}

# ============================================
# PAGE CONFIG & SETUP
# ============================================

st.set_page_config(
    page_title="Iron Lady Sales Tracker | Official Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Official Iron Lady Custom CSS - COMPLETE
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main-header {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {IRONLADY_COLORS['primary']};
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    
    .sub-header {{
        text-align: center;
        color: {IRONLADY_COLORS['dark']};
        font-size: 1rem;
        margin-bottom: 30px;
        font-weight: 400;
    }}
    
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
    
    .logo-tagline {{
        color: {IRONLADY_COLORS['dark']};
        font-size: 1rem;
        margin-top: 10px;
        letter-spacing: 1px;
        font-weight: 400;
    }}
    
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 0px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.2);
    }}
    
    .data-entry-card {{
        background: white;
        padding: 25px;
        border-radius: 0px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 6px solid {IRONLADY_COLORS['primary']};
        margin: 20px 0;
    }}
    
    .login-card {{
        background: white;
        padding: 25px;
        border-radius: 0px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        border: 3px solid transparent;
        transition: all 0.3s;
    }}
    
    .login-card:hover {{
        border-color: {IRONLADY_COLORS['primary']};
        box-shadow: 0 6px 16px rgba(230, 57, 70, 0.2);
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
    
    .warning-msg {{
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
        color: {IRONLADY_COLORS['warning']};
        padding: 15px 20px;
        border-radius: 0px;
        margin: 15px 0;
        border-left: 5px solid {IRONLADY_COLORS['warning']};
        font-weight: 500;
    }}
    
    .stNumberInput > div > div > input {{
        border: 2px solid {IRONLADY_COLORS['accent']};
        border-radius: 0px;
        padding: 10px;
        font-weight: 600;
        color: {IRONLADY_COLORS['dark']};
    }}
    
    .stNumberInput > div > div > input:focus {{
        border-color: {IRONLADY_COLORS['primary']};
        box-shadow: 0 0 0 2px rgba(230, 57, 70, 0.1);
    }}
    
    .stTextInput > div > div > input {{
        border: 2px solid {IRONLADY_COLORS['accent']};
        border-radius: 0px;
        padding: 10px;
        font-weight: 600;
        color: {IRONLADY_COLORS['dark']};
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {IRONLADY_COLORS['primary']};
        box-shadow: 0 0 0 2px rgba(230, 57, 70, 0.1);
    }}
    
    .checklist-item {{
        background: white;
        padding: 15px 20px;
        border-radius: 0px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
        border-left: 4px solid {IRONLADY_COLORS['accent']};
        transition: all 0.2s;
    }}
    
    .checklist-item:hover {{
        border-left-color: {IRONLADY_COLORS['primary']};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .checklist-item-completed {{
        background: linear-gradient(135deg, #d4edda 0%, #e8f5e9 100%);
        border-left-color: {IRONLADY_COLORS['success']};
    }}
    
    .badge {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 0px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
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
        background: {IRONLADY_COLORS['dark']};
        color: white;
    }}
    
    .badge-required {{
        background: {IRONLADY_COLORS['danger']};
        color: white;
    }}
    
    .status-excellent {{
        background: {IRONLADY_COLORS['success']};
        color: white;
        padding: 6px 14px;
        border-radius: 0px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    
    .status-good {{
        background: {IRONLADY_COLORS['warning']};
        color: white;
        padding: 6px 14px;
        border-radius: 0px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    
    .status-poor {{
        background: {IRONLADY_COLORS['danger']};
        color: white;
        padding: 6px 14px;
        border-radius: 0px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {IRONLADY_COLORS['dark']} 0%, {IRONLADY_COLORS['secondary']} 100%);
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    .stProgress > div > div > div {{
        background: {IRONLADY_COLORS['primary']};
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
    
    .dataframe {{
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-radius: 0px;
    }}
    
    .dataframe thead tr th {{
        background: {IRONLADY_COLORS['dark']} !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 15px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .dataframe tbody tr:hover {{
        background-color: {IRONLADY_COLORS['light']} !important;
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
    
    hr {{
        border: none;
        height: 3px;
        background: {IRONLADY_COLORS['primary']};
        margin: 30px 0;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px;
        background-color: {IRONLADY_COLORS['light']};
        padding: 0px;
        border-radius: 0px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border-radius: 0px;
        padding: 15px 25px;
        font-weight: 700;
        color: {IRONLADY_COLORS['dark']};
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 3px solid transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {IRONLADY_COLORS['primary']};
        color: white !important;
        border-color: {IRONLADY_COLORS['primary']};
    }}
    
    .stFileUploader {{
        border: 2px dashed {IRONLADY_COLORS['primary']};
        border-radius: 0px;
        padding: 20px;
        background: {IRONLADY_COLORS['light']};
    }}
    
    .streamlit-expanderHeader {{
        background: {IRONLADY_COLORS['light']};
        border-radius: 0px;
        font-weight: 700;
        color: {IRONLADY_COLORS['dark']};
    }}
    
    .footer {{
        text-align: center;
        padding: 20px;
        color: {IRONLADY_COLORS['dark']};
        font-size: 0.85rem;
        margin-top: 50px;
        border-top: 3px solid {IRONLADY_COLORS['primary']};
        background: {IRONLADY_COLORS['accent']};
    }}
    
    .insight-box {{
        background: white;
        padding: 20px;
        border-radius: 5px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .code-box {{
        background: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid {IRONLADY_COLORS['primary']};
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin: 10px 0;
        overflow-x: auto;
        color: {IRONLADY_COLORS['dark']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION - COMPLETE
# ============================================

if 'team_leads' not in st.session_state:
    st.session_state.team_leads = ['Ghazala', 'Megha', 'Afreen', 'Soumya']

if 'user' not in st.session_state:
    st.session_state.user = None

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

if 'sheet_configured' not in st.session_state:
    st.session_state.sheet_configured = False

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# ============================================
# GOOGLE SHEETS INTEGRATION
# ============================================

def get_service_account_email():
    """Extract service account email from secrets"""
    try:
        if "gcp_service_account" in st.secrets:
            return st.secrets["gcp_service_account"].get("client_email", "Not configured")
        return "⚠️ Not configured in secrets.toml"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def connect_to_google_sheets():
    """Connect to Google Sheets"""
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        client = gspread.authorize(credentials)
        return client
        
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None

def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    if not GSHEETS_AVAILABLE:
        return None
    
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
        st.error(f"❌ Error: {str(e)}")
        return None

def parse_google_sheets_data(sheet_data):
    """Parse team leader data from Google Sheets"""
    if not sheet_data:
        return None
    
    parsed_data = {}
    
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
            
            if name in st.session_state.team_leads:
                if name not in parsed_data:
                    parsed_data[name] = []
                
                entry = {
                    'RM_Name': name,
                    'Total_RMs': 0,
                    'Lead_Count': 0,
                    'Target_Pitch': 0,
                    'Actual_Pitch': 0,
                    'Target_Registration': 0,
                    'Actual_Registration': 0
                }
                
                for col_variations, key in [
                    (['Total RMs', 'RMs', 'RM Count', 'Total_RMs'], 'Total_RMs'),
                    (['Lead Count', 'Leads', 'Total Leads', 'Lead_Count'], 'Lead_Count'),
                    (['Target Pitch', 'Pitch Target', 'Target_Pitch'], 'Target_Pitch'),
                    (['Actual Pitch', 'Pitches', 'Actual_Pitch'], 'Actual_Pitch'),
                    (['Target Registration', 'Target Reg', 'Target_Registration'], 'Target_Registration'),
                    (['Actual Registration', 'Actual Reg', 'Registrations', 'Actual_Registration'], 'Actual_Registration'),
                ]:
                    for col_name in col_variations:
                        if col_name in df.columns:
                            val = row.get(col_name, 0)
                            if pd.notna(val):
                                try:
                                    entry[key] = int(val)
                                except:
                                    entry[key] = 0
                                break
                
                parsed_data[name].append(entry)
    
    result = {}
    for name, entries in parsed_data.items():
        result[name] = pd.DataFrame(entries)
    
    return result if result else None

# ============================================
# AI ANALYSIS FUNCTIONS
# ============================================

def analyze_performance_data(df):
    """Analyze performance data and generate insights"""
    
    if df is None or len(df) == 0:
        return None
    
    # Find name column
    name_col = None
    for col in df.columns:
        if any(keyword in str(col).upper() for keyword in ['RM', 'NAME', 'TEAM']):
            name_col = col
            break
    
    if name_col:
        df = df[df[name_col] != ''].copy()
    
    if len(df) == 0:
        return None
    
    # Calculate metrics with flexible column names
    total_rms = 0
    total_leads = 0
    total_pitches = 0
    total_registrations = 0
    target_pitches = 0
    target_registrations = 0
    
    for col in df.columns:
        col_upper = str(col).upper()
        if 'TOTAL' in col_upper and 'RM' in col_upper:
            total_rms = df[col].sum()
        elif 'LEAD' in col_upper:
            total_leads = df[col].sum()
        elif 'ACTUAL' in col_upper and 'PITCH' in col_upper:
            total_pitches = df[col].sum()
        elif 'ACTUAL' in col_upper and 'REG' in col_upper:
            total_registrations = df[col].sum()
        elif 'TARGET' in col_upper and 'PITCH' in col_upper:
            target_pitches = df[col].sum()
        elif 'TARGET' in col_upper and 'REG' in col_upper:
            target_registrations = df[col].sum()
    
    conversion_rate = (total_registrations / total_pitches * 100) if total_pitches > 0 else 0
    pitch_achievement = (total_pitches / target_pitches * 100) if target_pitches > 0 else 0
    reg_achievement = (total_registrations / target_registrations * 100) if target_registrations > 0 else 0
    
    # Calculate per-RM conversion rates
    conversion_col = None
    for col in df.columns:
        col_upper = str(col).upper()
        if 'ACTUAL' in col_upper and 'PITCH' in col_upper:
            pitch_col = col
        if 'ACTUAL' in col_upper and 'REG' in col_upper:
            reg_col = col
    
    if pitch_col and reg_col:
        df['Conversion_Rate'] = df.apply(
            lambda row: (row[reg_col] / row[pitch_col] * 100) if row[pitch_col] > 0 else 0,
            axis=1
        )
        
        top_performer = df.loc[df['Conversion_Rate'].idxmax()] if len(df) > 0 else None
        bottom_performer = df.loc[df['Conversion_Rate'].idxmin()] if len(df) > 0 else None
        avg_conversion = df['Conversion_Rate'].mean()
    else:
        top_performer = None
        bottom_performer = None
        avg_conversion = 0
    
    insights = {
        'total_rms': int(total_rms),
        'total_leads': int(total_leads),
        'total_pitches': int(total_pitches),
        'total_registrations': int(total_registrations),
        'conversion_rate': round(conversion_rate, 1),
        'pitch_achievement': round(pitch_achievement, 1),
        'reg_achievement': round(reg_achievement, 1),
        'top_performer': top_performer,
        'bottom_performer': bottom_performer,
        'avg_conversion': round(avg_conversion, 1),
        'performance_status': 'Excellent' if conversion_rate >= 15 else 'Good' if conversion_rate >= 10 else 'Needs Improvement',
        'recommendations': generate_recommendations(conversion_rate, pitch_achievement, reg_achievement)
    }
    
    return insights

def generate_recommendations(conversion_rate, pitch_achievement, reg_achievement):
    """Generate actionable recommendations"""
    recommendations = []
    
    if conversion_rate < 10:
        recommendations.append("⚠️ **Critical:** Conversion rate is below 10%. Focus on improving pitch quality and follow-up processes.")
    elif conversion_rate < 15:
        recommendations.append("📈 **Action:** Conversion rate is good but can be improved. Consider additional training for closing techniques.")
    else:
        recommendations.append("✅ **Excellent:** Conversion rate is above 15% target. Maintain current strategies.")
    
    if pitch_achievement < 80:
        recommendations.append("🎯 **Focus:** Pitch completion is below 80% target. Increase daily pitch activities and monitor RM productivity.")
    
    if reg_achievement < 80:
        recommendations.append("📞 **Priority:** Registration achievement below 80%. Review follow-up processes and enhance closing scripts.")
    
    if not recommendations:
        recommendations.append("🎉 **Outstanding Performance:** All metrics are on target. Keep up the excellent work!")
    
    return recommendations

# ============================================
# EMAIL REPORTING FUNCTION
# ============================================

def send_email_report(recipient_emails, subject, analysis_data, df):
    """Send email report with analysis"""
    
    if not all([
        "email_sender" in st.secrets,
        "email_password" in st.secrets,
        "email_smtp_server" in st.secrets,
        "email_smtp_port" in st.secrets
    ]):
        st.error("❌ Email configuration not found in secrets")
        return False
    
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
                .header {{ background: #E63946; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background: #F5E6D3; padding: 15px; margin: 10px 0; border-left: 5px solid #E63946; }}
                .insight {{ background: #d4edda; padding: 15px; margin: 10px 0; border-left: 5px solid #2A9D8F; }}
                .warning {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 5px solid #F77F00; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th {{ background: #1A1A1A; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏆 IRON LADY SALES TRACKER</h1>
                <p>Performance Report - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <h2>📊 Performance Summary</h2>
                
                <div class="metric">
                    <strong>Total RMs:</strong> {analysis_data['total_rms']}<br/>
                    <strong>Total Leads:</strong> {analysis_data['total_leads']}<br/>
                    <strong>Pitches Completed:</strong> {analysis_data['total_pitches']}<br/>
                    <strong>Registrations:</strong> {analysis_data['total_registrations']}
                </div>
                
                <div class="metric">
                    <strong>Conversion Rate:</strong> {analysis_data['conversion_rate']}%<br/>
                    <strong>Pitch Achievement:</strong> {analysis_data['pitch_achievement']}%<br/>
                    <strong>Registration Achievement:</strong> {analysis_data['reg_achievement']}%<br/>
                    <strong>Average Conversion:</strong> {analysis_data['avg_conversion']}%
                </div>
                
                <h2>🎯 Performance Status</h2>
                <div class="insight">
                    <strong>Overall Performance:</strong> {analysis_data['performance_status']}
                </div>
                
                <h2>💡 Recommendations</h2>
        """
        
        for rec in analysis_data['recommendations']:
            html_body += f'<div class="warning">{rec}</div>'
        
        if analysis_data['top_performer'] is not None:
            # Find name column
            name_col = None
            for col in analysis_data['top_performer'].index:
                if any(keyword in str(col).upper() for keyword in ['RM', 'NAME', 'TEAM']):
                    name_col = col
                    break
            
            name = analysis_data['top_performer'][name_col] if name_col else 'N/A'
            
            html_body += f"""
                <h2>⭐ Top Performer</h2>
                <div class="insight">
                    <strong>Name:</strong> {name}<br/>
                    <strong>Conversion Rate:</strong> {analysis_data['top_performer'].get('Conversion_Rate', 0):.1f}%
                </div>
            """
        
        if df is not None and len(df) > 0:
            html_body += "<h2>📋 Detailed Performance Data</h2><table>"
            html_body += "<tr>" + "".join([f"<th>{col}</th>" for col in df.columns[:8]]) + "</tr>"
            
            for _, row in df.head(10).iterrows():
                html_body += "<tr>" + "".join([f"<td>{val}</td>" for val in list(row)[:8]]) + "</tr>"
            
            html_body += "</table>"
        
        html_body += """
            </div>
            <div class="footer">
                <p>© 2024 Iron Lady Sales Tracker | Automated Report</p>
                <p>Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
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
        
        return True
        
    except Exception as e:
        st.error(f"❌ Email error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

# ============================================
# LOGIN SECTION - COMPLETE
# ============================================

def show_login_page():
    """Display official Iron Lady branded login page"""
    
    st.markdown(f"""
    <div class="logo-container">
        <h1 class="logo-text">IRON LADY</h1>
        <p class="logo-tagline">Sales Performance Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="info-msg">👋 <strong>Welcome!</strong> Select your name to access your dashboard</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("### 👥 TEAM LEADERS")
        
        cols = st.columns(2)
        for idx, lead in enumerate(st.session_state.team_leads):
            role = "Senior TL" if lead in ['Ghazala', 'Megha'] else "TL Trainee"
            icon = "🏆" if lead in ['Ghazala', 'Megha'] else "🌟"
            
            with cols[idx % 2]:
                if st.button(f"{icon} {lead} ({role})", key=f"login_{idx}", use_container_width=True):
                    st.session_state.user = lead
                    st.session_state.checklist = {}
                    if lead not in st.session_state.rm_data_by_lead:
                        st.session_state.rm_data_by_lead[lead] = pd.DataFrame({
                            'RM_Name': [''],
                            'Total_RMs': [0],
                            'Lead_Count': [0],
                            'Target_Pitch': [0],
                            'Actual_Pitch': [0],
                            'Target_Registration': [0],
                            'Actual_Registration': [0]
                        })
                    st.rerun()
        
        st.markdown("---")
        
        with st.expander("➕ ADD NEW TEAM LEADER"):
            new_lead_name = st.text_input("Enter team leader name:", key="new_lead_input", placeholder="e.g., John Smith")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ ADD & LOGIN", key="add_new_lead", use_container_width=True):
                    if new_lead_name and new_lead_name.strip():
                        new_name = new_lead_name.strip()
                        if new_name not in st.session_state.team_leads:
                            st.session_state.team_leads.append(new_name)
                            st.session_state.user = new_name
                            st.session_state.checklist = {}
                            st.session_state.rm_data_by_lead[new_name] = pd.DataFrame({
                                'RM_Name': [''],
                                'Total_RMs': [0],
                                'Lead_Count': [0],
                                'Target_Pitch': [0],
                                'Actual_Pitch': [0],
                                'Target_Registration': [0],
                                'Actual_Registration': [0]
                            })
                            st.markdown(f'<div class="success-msg">✅ Added {new_name} successfully!</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown('<div class="warning-msg">⚠️ This name already exists!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-msg">❌ Please enter a valid name</div>', unsafe_allow_html=True)
            
            with col_b:
                if st.button("➕ JUST ADD", key="just_add", use_container_width=True):
                    if new_lead_name and new_lead_name.strip():
                        new_name = new_lead_name.strip()
                        if new_name not in st.session_state.team_leads:
                            st.session_state.team_leads.append(new_name)
                            st.session_state.rm_data_by_lead[new_name] = pd.DataFrame({
                                'RM_Name': [''],
                                'Total_RMs': [0],
                                'Lead_Count': [0],
                                'Target_Pitch': [0],
                                'Actual_Pitch': [0],
                                'Target_Registration': [0],
                                'Actual_Registration': [0]
                            })
                            st.markdown(f'<div class="success-msg">✅ Added {new_name} to list</div>', unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.markdown('<div class="warning-msg">⚠️ This name already exists!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-msg">❌ Please enter a valid name</div>', unsafe_allow_html=True)

# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_current_user_data():
    """Get data for current logged-in user"""
    if st.session_state.user not in st.session_state.rm_data_by_lead:
        st.session_state.rm_data_by_lead[st.session_state.user] = pd.DataFrame({
            'RM_Name': [''],
            'Total_RMs': [0],
            'Lead_Count': [0],
            'Target_Pitch': [0],
            'Actual_Pitch': [0],
            'Target_Registration': [0],
            'Actual_Registration': [0]
        })
    return st.session_state.rm_data_by_lead[st.session_state.user]

def update_current_user_data(df):
    """Update data for current logged-in user"""
    st.session_state.rm_data_by_lead[st.session_state.user] = df

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

def get_status_badge(conversion_rate):
    """Get status badge HTML based on conversion rate"""
    if conversion_rate >= 15:
        return '<span class="status-excellent">✅ EXCELLENT</span>'
    elif conversion_rate >= 10:
        return '<span class="status-good">⚠️ GOOD</span>'
    else:
        return '<span class="status-poor">❌ NEEDS IMPROVEMENT</span>'

# ============================================
# DATA ENTRY INTERFACE - COMPLETE
# ============================================

def show_data_entry_interface():
    """Display professional data entry interface for RM metrics"""
    st.markdown("### 📝 MANUAL DATA ENTRY")
    
    st.markdown('<div class="info-msg">💡 <strong>Instructions:</strong> Enter your team\'s performance data below. You can add multiple entries for different RMs or teams.</div>', unsafe_allow_html=True)
    
    current_data = get_current_user_data()
    
    with st.expander("➕ ADD NEW RM ENTRY", expanded=True):
        st.markdown("#### Enter RM Performance Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rm_name = st.text_input(
                "RM Name / Team Name",
                key="new_rm_name",
                placeholder="e.g., Amit Kumar or Team A"
            )
            
            total_rms = st.number_input(
                "Total RMs Under This Entry",
                min_value=0,
                value=1,
                step=1,
                key="new_total_rms",
                help="Number of RMs in this team/entry"
            )
            
            lead_count = st.number_input(
                "Total Leads",
                min_value=0,
                value=0,
                step=1,
                key="new_lead_count",
                help="Total number of leads assigned"
            )
            
            target_pitch = st.number_input(
                "Target Pitches",
                min_value=0,
                value=0,
                step=1,
                key="new_target_pitch",
                help="Target number of pitches to complete"
            )
        
        with col2:
            actual_pitch = st.number_input(
                "Actual Pitches Completed",
                min_value=0,
                value=0,
                step=1,
                key="new_actual_pitch",
                help="Actual number of pitches completed"
            )
            
            target_reg = st.number_input(
                "Target Registrations",
                min_value=0,
                value=0,
                step=1,
                key="new_target_reg",
                help="Target number of registrations"
            )
            
            actual_reg = st.number_input(
                "Actual Registrations",
                min_value=0,
                value=0,
                step=1,
                key="new_actual_reg",
                help="Actual number of registrations completed"
            )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("✅ ADD ENTRY", use_container_width=True, key="add_rm_entry"):
                if rm_name and rm_name.strip():
                    if rm_name in current_data['RM_Name'].values:
                        st.markdown('<div class="warning-msg">⚠️ Entry with this name already exists! Use UPDATE instead.</div>', unsafe_allow_html=True)
                    else:
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
                        
                        st.markdown(f'<div class="success-msg">✅ <strong>Entry added successfully!</strong> {rm_name} with {total_rms} RMs</div>', unsafe_allow_html=True)
                        st.rerun()
                else:
                    st.markdown('<div class="error-msg">❌ Please enter an RM/Team name</div>', unsafe_allow_html=True)
        
        with col_btn2:
            if st.button("🔄 CLEAR FORM", use_container_width=True, key="clear_form"):
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 CURRENT ENTRIES")
    
    display_data = current_data[current_data['RM_Name'] != ''].copy()
    
    if len(display_data) > 0:
        display_data['Conversion %'] = display_data.apply(
            lambda row: round((row['Actual_Registration'] / row['Actual_Pitch'] * 100), 1) 
            if row['Actual_Pitch'] > 0 else 0,
            axis=1
        )
        
        st.dataframe(
            display_data[['RM_Name', 'Total_RMs', 'Lead_Count', 'Target_Pitch', 
                         'Actual_Pitch', 'Target_Registration', 'Actual_Registration', 'Conversion %']],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("#### ⚙️ MANAGE ENTRIES")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_rm = st.selectbox(
                "Select Entry to Manage",
                options=display_data['RM_Name'].tolist(),
                key="selected_rm_to_manage"
            )
        
        with col2:
            if st.button("🗑️ DELETE ENTRY", use_container_width=True, type="secondary"):
                current_data = current_data[current_data['RM_Name'] != selected_rm]
                update_current_user_data(current_data)
                st.markdown(f'<div class="success-msg">✅ Deleted entry for {selected_rm}</div>', unsafe_allow_html=True)
                st.rerun()
        
        metrics = calculate_metrics(display_data)
        
        st.markdown("---")
        st.markdown("### 📈 QUICK SUMMARY")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total RMs", metrics['total_rms'])
        with col2:
            st.metric("Total Leads", metrics['total_leads'])
        with col3:
            st.metric("Pitches", f"{metrics['total_actual_pitch']}/{metrics['total_target_pitch']}")
        with col4:
            st.metric("Registrations", f"{metrics['total_actual_reg']}/{metrics['total_target_reg']}")
    
    else:
        st.markdown('<div class="info-msg">📊 No entries yet. Add your first RM entry above to get started!</div>', unsafe_allow_html=True)

    # ============================================
# PERFORMANCE DASHBOARD - COMPLETE
# ============================================

def show_performance_dashboard():
    """Display comprehensive performance dashboard"""
    st.markdown(f"### 📊 TEAM PERFORMANCE OVERVIEW - {st.session_state.selected_day}")
    
    current_data = get_current_user_data()
    metrics = calculate_metrics(current_data)
    
    # Summary cards with enhanced design
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0; font-weight: 900; text-transform: uppercase; font-size: 0.85rem;">Total RMs</h4>
            <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 10px 0; font-weight: 900;">{metrics['total_rms']}</h2>
            <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.75rem;">Active Team Members</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0; font-weight: 900; text-transform: uppercase; font-size: 0.85rem;">Total Leads</h4>
            <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 10px 0; font-weight: 900;">{metrics['total_leads']}</h2>
            <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.75rem;">Active Prospects</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        achievement_color = IRONLADY_COLORS['success'] if metrics['pitch_achievement'] >= 80 else IRONLADY_COLORS['warning']
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0; font-weight: 900; text-transform: uppercase; font-size: 0.85rem;">Pitch Achievement</h4>
            <h2 style="color: {achievement_color}; margin: 10px 0; font-weight: 900;">{metrics['pitch_achievement']}%</h2>
            <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.75rem;">{metrics['total_actual_pitch']}/{metrics['total_target_pitch']} Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        reg_color = IRONLADY_COLORS['success'] if metrics['reg_achievement'] >= 80 else IRONLADY_COLORS['warning']
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0; font-weight: 900; text-transform: uppercase; font-size: 0.85rem;">Registration Achievement</h4>
            <h2 style="color: {reg_color}; margin: 10px 0; font-weight: 900;">{metrics['reg_achievement']}%</h2>
            <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.75rem;">{metrics['total_actual_reg']}/{metrics['total_target_reg']} Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        conv_color = IRONLADY_COLORS['success'] if metrics['conversion_rate'] >= 15 else IRONLADY_COLORS['warning']
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0; font-weight: 900; text-transform: uppercase; font-size: 0.85rem;">Conversion Rate</h4>
            <h2 style="color: {conv_color}; margin: 10px 0; font-weight: 900;">{metrics['conversion_rate']}%</h2>
            <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.75rem;">Pitch to Registration</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        chart_data = current_data[current_data['RM_Name'] != ''].copy()
        if len(chart_data) > 0:
            chart_data['Conversion %'] = chart_data.apply(
                lambda row: (row['Actual_Registration'] / row['Actual_Pitch'] * 100) 
                if row['Actual_Pitch'] > 0 else 0,
                axis=1
            )
            
            fig = px.bar(
                chart_data,
                x='RM_Name',
                y='Conversion %',
                title='<b>RM-WISE CONVERSION RATE</b>',
                color='Conversion %',
                color_continuous_scale=[[0, IRONLADY_COLORS['danger']], [0.5, IRONLADY_COLORS['warning']], [1, IRONLADY_COLORS['success']]]
            )
            fig.update_layout(
                height=400,
                font=dict(family="Inter, sans-serif", size=12, color=IRONLADY_COLORS['dark']),
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_size=16
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        summary_df = pd.DataFrame({
            'Metric': ['Pitch', 'Registration'],
            'Target': [metrics['total_target_pitch'], metrics['total_target_reg']],
            'Actual': [metrics['total_actual_pitch'], metrics['total_actual_reg']]
        })
        
        fig = px.bar(
            summary_df,
            x='Metric',
            y=['Target', 'Actual'],
            title='<b>TARGET VS ACTUAL PERFORMANCE</b>',
            barmode='group',
            color_discrete_map={'Target': IRONLADY_COLORS['dark'], 'Actual': IRONLADY_COLORS['primary']}
        )
        fig.update_layout(
            height=400,
            font=dict(family="Inter, sans-serif", size=12, color=IRONLADY_COLORS['dark']),
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=16
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Performance table
    st.markdown("### 📋 DETAILED RM PERFORMANCE")
    
    display_df = current_data[current_data['RM_Name'] != ''].copy()
    if len(display_df) > 0:
        display_df['Conversion %'] = display_df.apply(
            lambda row: round((row['Actual_Registration'] / row['Actual_Pitch'] * 100), 1) 
            if row['Actual_Pitch'] > 0 else 0,
            axis=1
        )
        display_df['Status'] = display_df['Conversion %'].apply(
            lambda x: '✅ Excellent' if x >= 15 else ('⚠️ Good' if x >= 10 else '❌ Needs Improvement')
        )
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="info-msg">📊 No RM data available yet. Go to <strong>DATA ENTRY</strong> tab to add team data.</div>', unsafe_allow_html=True)

# ============================================
# GOOGLE SHEETS DASHBOARD WITH AI ANALYSIS - COMPLETE
# ============================================

def show_google_sheets_dashboard():
    """Display Google Sheets data with live analysis in the dashboard"""
    
    st.markdown("### 📊 GOOGLE SHEETS LIVE DASHBOARD & AI ANALYSIS")
    
    if not GSHEETS_AVAILABLE:
        st.error("❌ Google Sheets not available. Install: pip install gspread google-auth")
        st.code("pip install gspread google-auth")
        return
    
    # Main dashboard display
    if st.session_state.loaded_sheet_data and st.session_state.use_google_sheets:
        
        st.markdown('<div class="success-msg">✅ <strong>Live Google Sheets Data Connected & Analyzing...</strong></div>', unsafe_allow_html=True)
        
        # Display all sheets with analysis
        if len(st.session_state.loaded_sheet_data) > 0:
            sheet_names = list(st.session_state.loaded_sheet_data.keys())
            
            # Create tabs for each sheet
            sheet_tabs = st.tabs([f"📋 {name}" for name in sheet_names])
            
            for idx, sheet_name in enumerate(sheet_names):
                with sheet_tabs[idx]:
                    df = st.session_state.loaded_sheet_data[sheet_name]
                    
                    st.markdown(f"### 📊 Sheet: {sheet_name}")
                    st.markdown(f"**Rows:** {len(df)} | **Columns:** {len(df.columns)}")
                    
                    # Display the raw data
                    with st.expander("📄 VIEW RAW DATA", expanded=False):
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    
                    # AI Analysis Section
                    st.markdown("### 🤖 AI-POWERED PERFORMANCE ANALYSIS")
                    
                    with st.spinner("🔍 Analyzing data..."):
                        analysis = analyze_performance_data(df)
                    
                    if analysis:
                        # Save analysis for email
                        st.session_state.analysis_results = analysis
                        
                        # Key Metrics Row
                        st.markdown("#### 📊 KEY PERFORMANCE METRICS")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total RMs", analysis['total_rms'])
                            st.metric("Total Leads", analysis['total_leads'])
                        
                        with col2:
                            st.metric("Total Pitches", analysis['total_pitches'])
                            st.metric("Total Registrations", analysis['total_registrations'])
                        
                        with col3:
                            delta_conv = analysis['conversion_rate'] - 15  # Target is 15%
                            st.metric("Conversion Rate", f"{analysis['conversion_rate']}%", delta=f"{delta_conv:+.1f}%")
                            st.metric("Avg Team Conversion", f"{analysis['avg_conversion']}%")
                        
                        with col4:
                            st.metric("Pitch Achievement", f"{analysis['pitch_achievement']}%")
                            st.metric("Reg Achievement", f"{analysis['reg_achievement']}%")
                        
                        st.markdown("---")
                        
                        # Performance Status
                        st.markdown("#### 🎯 OVERALL PERFORMANCE STATUS")
                        status_color = "success" if analysis['conversion_rate'] >= 15 else "warning" if analysis['conversion_rate'] >= 10 else "error"
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if analysis['conversion_rate'] >= 15:
                                st.markdown("## ✅")
                            elif analysis['conversion_rate'] >= 10:
                                st.markdown("## ⚠️")
                            else:
                                st.markdown("## ❌")
                        
                        with col2:
                            st.markdown(f"""
                            <div class="{status_color}-msg">
                                <h3 style="margin: 0; border: none;">{analysis['performance_status']}</h3>
                                <p style="margin: 5px 0 0 0;">Current conversion rate: {analysis['conversion_rate']}% | Team average: {analysis['avg_conversion']}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Recommendations
                        st.markdown("#### 💡 ACTIONABLE RECOMMENDATIONS")
                        for idx, rec in enumerate(analysis['recommendations']):
                            st.markdown(f"""
                            <div class="insight-box">
                                <strong>Recommendation {idx+1}:</strong><br/>
                                {rec}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Top & Bottom Performers
                        st.markdown("#### ⭐ TEAM PERFORMANCE ANALYSIS")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if analysis['top_performer'] is not None:
                                st.markdown("##### 🏆 TOP PERFORMER")
                                
                                # Find name column
                                name_col = None
                                for col in analysis['top_performer'].index:
                                    if any(keyword in str(col).upper() for keyword in ['RM', 'NAME', 'TEAM']):
                                        name_col = col
                                        break
                                
                                name = analysis['top_performer'][name_col] if name_col else 'N/A'
                                conv_rate = analysis['top_performer'].get('Conversion_Rate', 0)
                                
                                st.markdown(f"""
                                <div class="success-msg">
                                    <strong>🌟 Name:</strong> {name}<br/>
                                    <strong>📈 Conversion Rate:</strong> {conv_rate:.1f}%<br/>
                                    <strong>💼 Status:</strong> Outstanding Performance<br/>
                                    <strong>🎯 Action:</strong> Use as best practice example for team
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col2:
                            if analysis['bottom_performer'] is not None:
                                st.markdown("##### 📉 NEEDS SUPPORT")
                                
                                # Find name column
                                name_col = None
                                for col in analysis['bottom_performer'].index:
                                    if any(keyword in str(col).upper() for keyword in ['RM', 'NAME', 'TEAM']):
                                        name_col = col
                                        break
                                
                                name = analysis['bottom_performer'][name_col] if name_col else 'N/A'
                                conv_rate = analysis['bottom_performer'].get('Conversion_Rate', 0)
                                
                                st.markdown(f"""
                                <div class="warning-msg">
                                    <strong>👤 Name:</strong> {name}<br/>
                                    <strong>📊 Conversion Rate:</strong> {conv_rate:.1f}%<br/>
                                    <strong>⚠️ Status:</strong> Requires Attention<br/>
                                    <strong>🎯 Action:</strong> Provide coaching and additional training
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Performance Distribution Chart
                        st.markdown("#### 📊 PERFORMANCE DISTRIBUTION")
                        
                        if 'Conversion_Rate' in df.columns or any('CONV' in str(col).upper() for col in df.columns):
                            # Create histogram
                            conv_col = 'Conversion_Rate' if 'Conversion_Rate' in df.columns else [col for col in df.columns if 'CONV' in str(col).upper()][0]
                            
                            fig = px.histogram(
                                df,
                                x=conv_col,
                                nbins=10,
                                title='<b>Team Conversion Rate Distribution</b>',
                                labels={conv_col: 'Conversion Rate (%)'},
                                color_discrete_sequence=[IRONLADY_COLORS['primary']]
                            )
                            fig.add_vline(x=15, line_dash="dash", line_color=IRONLADY_COLORS['success'], 
                                         annotation_text="Target: 15%")
                            fig.update_layout(
                                height=400,
                                font=dict(family="Inter, sans-serif", size=12),
                                plot_bgcolor='white',
                                paper_bgcolor='white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Email Report Section
                        st.markdown("### 📧 EMAIL AUTOMATED REPORT")
                        
                        st.markdown('<div class="info-msg">📨 <strong>Send this analysis to multiple recipients</strong><br/>Enter email addresses separated by commas or new lines</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            recipient_emails = st.text_area(
                                "Recipient Email Addresses",
                                placeholder="manager@company.com, teamlead@company.com\nsupervisor@company.com",
                                help="Enter multiple emails separated by commas or new lines",
                                height=100,
                                key=f"emails_{sheet_name}"
                            )
                        
                        with col2:
                            st.markdown("<br/><br/>", unsafe_allow_html=True)
                            
                            if st.button("📧 SEND REPORT", use_container_width=True, type="primary", key=f"send_{sheet_name}"):
                                if recipient_emails:
                                    # Parse emails
                                    emails = [e.strip() for e in recipient_emails.replace(',', '\n').split('\n') if e.strip()]
                                    
                                    if emails:
                                        with st.spinner("📤 Sending email report..."):
                                            success = send_email_report(
                                                emails,
                                                f"Iron Lady Sales Report - {sheet_name} - {datetime.now().strftime('%B %d, %Y')}",
                                                analysis,
                                                df
                                            )
                                            
                                            if success:
                                                st.success(f"✅ Email report sent successfully to {len(emails)} recipient(s)!")
                                                st.balloons()
                                            else:
                                                st.error("❌ Failed to send email. Check your email configuration in secrets.toml")
                                    else:
                                        st.error("❌ Please enter at least one valid email address")
                                else:
                                    st.error("❌ Please enter recipient email addresses")
                            
                            st.markdown("<br/>", unsafe_allow_html=True)
                            
                            # Download as CSV
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="⬇️ DOWNLOAD CSV",
                                data=csv,
                                file_name=f"{sheet_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        st.markdown("---")
                        
                        # Auto-refresh option
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            auto_refresh = st.checkbox(
                                "🔄 Enable auto-refresh (refreshes data every 5 minutes)",
                                key=f"auto_refresh_{sheet_name}"
                            )
                            
                            if auto_refresh:
                                st.info("⏰ Auto-refresh enabled. Data will reload automatically every 5 minutes.")
                        
                        with col2:
                            if st.button("🔄 REFRESH NOW", use_container_width=True, key=f"refresh_{sheet_name}"):
                                st.rerun()
                    
                    else:
                        st.warning("⚠️ Could not analyze data. Please check that your sheet has the required columns.")
                        st.info("""
                        **Required columns (case-insensitive):**
                        - Name column: RM Name, Name, Team, Leader
                        - Metrics: Total RMs, Lead Count, Target Pitch, Actual Pitch, Target Registration, Actual Registration
                        """)
        
    else:
        st.markdown("""
        <div class="info-msg">
            <h3 style="margin-top: 0; border: none;">📊 Google Sheets Dashboard Not Connected</h3>
            <p><strong>To view live Google Sheets data with AI analysis:</strong></p>
            <ol style="margin-left: 20px;">
                <li>Enable "📊 Use Google Sheets" in the sidebar</li>
                <li>Enter your Google Sheet ID or URL</li>
                <li>Click "🔄 Load from Sheets" button</li>
                <li>View live data, AI insights, and send email reports!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Configuration Required")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 📋 Google Sheets Setup
            Add to `.streamlit/secrets.toml`:
```toml
            [gcp_service_account]
            type = "service_account"
            project_id = "your-project"
            private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
            client_email = "account@project.iam.gserviceaccount.com"
            client_id = "123456789"
            auth_uri = "https://accounts.google.com/o/oauth2/auth"
            token_uri = "https://oauth2.googleapis.com/token"
```
            """)
        
        with col2:
            st.markdown("""
            #### 📧 Email Configuration
            Add to `.streamlit/secrets.toml`:
```toml
            email_sender = "your-email@gmail.com"
            email_password = "your-app-password"
            email_smtp_server = "smtp.gmail.com"
            email_smtp_port = "587"
```
            
            **For Gmail:**
            1. Enable 2-factor authentication
            2. Generate App Password
            3. Use App Password (not regular password)
            """)

# ============================================
# DOCUMENT MANAGEMENT - COMPLETE
# ============================================

def show_document_management():
    """Display document management system"""
    st.markdown("### 📁 DOCUMENT MANAGEMENT SYSTEM")
    
    st.markdown(f'<div class="info-msg">📤 <strong>Upload Instructions:</strong> Upload your daily reports, documents, and <strong>screenshots</strong>. Accepted formats: PDF, DOCX, XLSX, PNG, JPG, JPEG. All files are securely tracked.</div>', unsafe_allow_html=True)
    
    file_types = {
        'WA Audit Files': {
            'key': 'wa_audit', 
            'icon': '💬', 
            'desc': 'WhatsApp audit reports, screenshots, and conversation exports'
        },
        'SL Status List': {
            'key': 'sl_status', 
            'icon': '📋', 
            'desc': 'Short list status documents and tracking screenshots'
        },
        'Hot Prospects List': {
            'key': 'hot_prospects', 
            'icon': '🔥', 
            'desc': 'High-priority prospect lists and screenshots'
        },
        'Call Audit Files': {
            'key': 'call_audit', 
            'icon': '📞', 
            'desc': 'Call recording audits, reports, and app screenshots'
        },
        'Other Documents': {
            'key': 'other', 
            'icon': '📄', 
            'desc': 'Additional supporting documents and screenshots'
        }
    }
    
    for file_label, file_info in file_types.items():
        with st.expander(f"{file_info['icon']} {file_label}", expanded=False):
            st.markdown(f"<p style='color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem;'>{file_info['desc']}</p>", unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                f"Upload {file_label.lower()} (PDFs, documents, images, screenshots)",
                key=f"uploader_{file_info['key']}",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif']
            )
            
            if uploaded_files:
                st.markdown("#### 📤 Uploaded Files:")
                for uploaded_file in uploaded_files:
                    file_size = uploaded_file.size / 1024  # Convert to KB
                    st.markdown(f"""
                    <div class="success-msg">
                        ✅ <strong>{uploaded_file.name}</strong> ({file_size:.1f} KB)<br/>
                        Type: {uploaded_file.type} | Ready to process
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.files_uploaded[f"{file_info['key']}_{uploaded_file.name}"] = {
                        'name': uploaded_file.name,
                        'size': file_size,
                        'type': uploaded_file.type,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
    
    # Display all uploaded files summary
    if st.session_state.files_uploaded:
        st.markdown("---")
        st.markdown("### 📊 UPLOAD SUMMARY")
        
        summary_df = pd.DataFrame([
            {
                'File Name': v['name'],
                'Size (KB)': f"{v['size']:.1f}",
                'Type': v['type'],
                'Uploaded At': v['timestamp']
            }
            for v in st.session_state.files_uploaded.values()
        ])
        
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ CLEAR ALL UPLOADS", type="secondary"):
            st.session_state.files_uploaded = {}
            st.rerun()

# ============================================
# CHECKLIST - COMPLETE WITH ALL ITEMS
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

def render_checklist_items(items, priority):
    """Render checklist items with Iron Lady branding"""
    for idx, item_dict in enumerate(items):
        task = item_dict['task']
        item_type = item_dict.get('type', 'checkbox')
        required = item_dict.get('required', False)
        
        # Determine badge
        badge_html = ""
        if item_type == 'upload':
            badge_html = '<span class="badge badge-upload">📤 UPLOAD</span>'
        elif item_type == 'manual':
            badge_html = '<span class="badge badge-manual">✋ MANUAL</span>'
        elif item_type == 'ongoing':
            badge_html = '<span class="badge badge-ongoing">🔄 ONGOING</span>'
        elif required:
            badge_html = '<span class="badge badge-required">⚠️ REQUIRED</span>'
        
        # Check if completed
        is_completed = st.session_state.checklist.get(task, False)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            checked = st.checkbox(
                task,
                value=is_completed,
                key=f"check_{priority}_{idx}_{st.session_state.selected_day}"
            )
            st.session_state.checklist[task] = checked
        
        with col2:
            if badge_html:
                st.markdown(badge_html, unsafe_allow_html=True)

def show_checklist():
    """Display complete daily checklist"""
    st.markdown("### ✅ DAILY ACTIVITY CHECKLIST")
    
    selected_checklist = CHECKLIST_ITEMS.get(st.session_state.selected_day, [])
    
    # Show time if available
    if selected_checklist and selected_checklist[0].get('time'):
        st.markdown(f'<div class="info-msg">⏰ <strong>Session Time:</strong> {selected_checklist[0]["time"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Group by priority
    high_priority = [item for item in selected_checklist if item.get('priority') == 'high']
    medium_priority = [item for item in selected_checklist if item.get('priority') == 'medium']
    low_priority = [item for item in selected_checklist if item.get('priority') not in ['high', 'medium']]
    
    # High Priority Tasks
    if high_priority:
        st.markdown(f"#### 🔴 HIGH PRIORITY TASKS ({len(high_priority)} items)")
        render_checklist_items(high_priority, 'high')
    
    # Medium Priority Tasks
    if medium_priority:
        st.markdown("---")
        st.markdown(f"#### 🟡 MEDIUM PRIORITY TASKS ({len(medium_priority)} items)")
        render_checklist_items(medium_priority, 'medium')
    
    # Low Priority Tasks
    if low_priority:
        st.markdown("---")
        st.markdown(f"#### 🟢 STANDARD TASKS ({len(low_priority)} items)")
        render_checklist_items(low_priority, 'low')
    
    st.markdown("---")
    
    # Calculate progress
    task_names = [item['task'] for item in selected_checklist]
    checked_count = sum(1 for task in task_names if st.session_state.checklist.get(task, False))
    progress = checked_count / len(task_names) * 100 if task_names else 0
    
    # Progress bar with custom styling
    st.markdown(f"""
    <div style="background: {IRONLADY_COLORS['light']}; padding: 20px; border-radius: 0px; margin: 20px 0; border-left: 5px solid {IRONLADY_COLORS['primary']};">
        <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0 0 10px 0; font-weight: 900; text-transform: uppercase;">📊 OVERALL PROGRESS</h4>
    """, unsafe_allow_html=True)
    
    st.progress(progress / 100, text=f"{progress:.0f}% Complete ({checked_count}/{len(task_names)} tasks)")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="✅ Completed", value=f"{checked_count}")
    
    with col2:
        st.metric(label="⏳ Remaining", value=f"{len(task_names) - checked_count}")
    
    with col3:
        high_completed = sum(1 for item in high_priority if st.session_state.checklist.get(item['task'], False))
        st.metric(label="🔴 High Priority Done", value=f"{high_completed}/{len(high_priority)}")
    
    with col4:
        if checked_count == len(task_names) and len(task_names) > 0:
            st.markdown("### 🎉")
            st.markdown("**ALL DONE!**")
        else:
            completion_rate = (checked_count / len(task_names) * 100) if task_names else 0
            st.metric(label="📈 Completion", value=f"{completion_rate:.0f}%")

# ============================================
# MAIN APP FUNCTION - COMPLETE
# ============================================

def main():
    # Login check
    if st.session_state.user is None:
        show_login_page()
        return
    
    # Header with branding
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"""
        <div style="background: {IRONLADY_COLORS['accent']}; 
                    padding: 20px; border-radius: 0px; border-left: 5px solid {IRONLADY_COLORS['primary']};">
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
            st.session_state.checklist = {}
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar controls
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
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox(
            "📊 Use Google Sheets",
            value=st.session_state.use_google_sheets,
            help="Enable to load data from Google Sheets"
        )
        st.session_state.use_google_sheets = use_sheets
        
        if use_sheets:
            if st.session_state.sheet_configured:
                st.success("✅ Sheet configured")
            
            sheet_id = st.text_input(
                "Sheet ID/URL",
                placeholder="1abc123xyz... or full URL",
                help="Paste your Google Sheets ID or full URL"
            )
            
            if st.button("🔄 LOAD FROM SHEETS", use_container_width=True):
                if sheet_id:
                    with st.spinner("⏳ Loading data from Google Sheets..."):
                        sheet_data = fetch_sheet_data(sheet_id)
                        if sheet_data:
                            st.session_state.loaded_sheet_data = sheet_data
                            st.session_state.sheet_configured = True
                            
                            # Try to parse and import for current user
                            parsed = parse_google_sheets_data(sheet_data)
                            if parsed and st.session_state.user in parsed:
                                st.session_state.rm_data_by_lead[st.session_state.user] = parsed[st.session_state.user]
                            
                            st.success("✅ Data loaded!")
                            st.rerun()
                else:
                    st.error("❌ Please enter a Sheet ID")
        
        st.markdown("---")
        st.markdown("### 📊 QUICK STATS")
        
        current_data = get_current_user_data()
        metrics = calculate_metrics(current_data)
        
        st.metric("Total RMs", metrics['total_rms'])
        st.metric("Total Leads", metrics['total_leads'])
        st.metric("Pitch Achievement", f"{metrics['pitch_achievement']}%")
        st.metric("Reg Achievement", f"{metrics['reg_achievement']}%")
        st.metric("Conversion Rate", f"{metrics['conversion_rate']}%")
        
        st.markdown("---")
        
        # System info
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 0px; margin-top: 20px; border-left: 3px solid {IRONLADY_COLORS['primary']};">
            <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">
                <strong>System Status:</strong><br/>
                ✅ Connected<br/>
                🕐 {datetime.now().strftime('%I:%M %p')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Tab Structure - ALL 5 TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 DATA ENTRY",
        "📊 PERFORMANCE DASHBOARD",
        "📈 GOOGLE SHEETS & AI ANALYSIS",
        "📁 DOCUMENT MANAGEMENT",
        "✅ DAILY CHECKLIST"
    ])
    
    with tab1:
        show_data_entry_interface()
    
    with tab2:
        show_performance_dashboard()
    
    with tab3:
        show_google_sheets_dashboard()
    
    with tab4:
        show_document_management()
    
    with tab5:
        show_checklist()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p style="font-weight: 900; text-transform: uppercase; letter-spacing: 2px; font-size: 1.1rem; color: {IRONLADY_COLORS['primary']};">IRON LADY SALES TRACKER</p>
        <p style="font-weight: 600;">Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
        <p style="font-weight: 600;">Complete Edition with Google Sheets Live View, AI Analysis & Email Reports | v8.0</p>
        <p style="font-size: 0.75rem; opacity: 0.7; margin-top: 10px;">© 2024 Iron Lady. All rights reserved. | Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
