"""
IRON LADY - COMPLETE SALES DASHBOARD
Real-time sales performance tracking with Google Sheets, AI Analysis & Email Reports
Team: Ghazala, Megha, Afreen, Soumya
Version: 9.0 Complete Edition
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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
</style>
""", unsafe_allow_html=True)

# ============================================
# TEAM LEADERS
# ============================================

TEAM_LEADERS = ['Ghazala', 'Megha', 'Afreen', 'Soumya']

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

@st.cache_resource
def connect_to_google_sheets():
    """Connect to Google Sheets using Streamlit secrets"""
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
        st.error(f"❌ Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)
def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    try:
        client = connect_to_google_sheets()
        if not client:
            return None
        
        # Extract sheet ID from URL if needed
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

def parse_team_data(sheet_data):
    """Parse team leader data from Google Sheets"""
    if not sheet_data:
        return None
    
    team_data = []
    
    for sheet_name, df in sheet_data.items():
        # Find name column
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
            
            if name in TEAM_LEADERS:
                # Extract data with multiple column name variations
                entry = {
                    'name': name,
                    'rms': 0,
                    'leads': 0,
                    'pitches_target': 0,
                    'pitches_actual': 0,
                    'reg_target': 0,
                    'reg_actual': 0,
                }
                
                # Try different column name variations
                for col in df.columns:
                    col_upper = str(col).upper()
                    val = row.get(col, 0)
                    
                    try:
                        val = int(val) if pd.notna(val) else 0
                    except:
                        val = 0
                    
                    if 'TOTAL' in col_upper and 'RM' in col_upper:
                        entry['rms'] = val
                    elif 'LEAD' in col_upper and 'COUNT' in col_upper:
                        entry['leads'] = val
                    elif 'TARGET' in col_upper and 'PITCH' in col_upper:
                        entry['pitches_target'] = val
                    elif 'ACTUAL' in col_upper and 'PITCH' in col_upper:
                        entry['pitches_actual'] = val
                    elif 'TARGET' in col_upper and 'REG' in col_upper:
                        entry['reg_target'] = val
                    elif 'ACTUAL' in col_upper and 'REG' in col_upper:
                        entry['reg_actual'] = val
                
                # Calculate achievements
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
# AI ANALYSIS FUNCTIONS
# ============================================

def analyze_team_performance(df):
    """Generate AI-powered insights from team data"""
    
    insights = {
        'total_rms': int(df['rms'].sum()),
        'total_leads': int(df.get('leads', pd.Series([0])).sum()),
        'total_pitches': int(df['pitches_actual'].sum()),
        'total_registrations': int(df['reg_actual'].sum()),
        'avg_conversion': round(df['conversion'].mean(), 1),
        'avg_pitch_achievement': round(df['pitch_achievement'].mean(), 1),
        'avg_reg_achievement': round(df['reg_achievement'].mean(), 1),
        'best_performer': None,
        'needs_support': None,
        'recommendations': []
    }
    
    # Find best and worst performers
    if len(df) > 0:
        best_idx = df['conversion'].idxmax()
        worst_idx = df['conversion'].idxmin()
        
        insights['best_performer'] = {
            'name': df.loc[best_idx, 'name'],
            'conversion': df.loc[best_idx, 'conversion'],
            'pitches': df.loc[best_idx, 'pitches_actual'],
            'registrations': df.loc[best_idx, 'reg_actual']
        }
        
        insights['needs_support'] = {
            'name': df.loc[worst_idx, 'name'],
            'conversion': df.loc[worst_idx, 'conversion'],
            'pitches': df.loc[worst_idx, 'pitches_actual'],
            'registrations': df.loc[worst_idx, 'reg_actual']
        }
    
    # Generate smart recommendations
    avg_conv = insights['avg_conversion']
    
    if avg_conv < 50:
        insights['recommendations'].append("🚨 **CRITICAL:** Team average conversion is critically low (<50%). Immediate intervention required - review pitch scripts, provide intensive training, and implement daily coaching sessions.")
    elif avg_conv < 60:
        insights['recommendations'].append("⚠️ **URGENT:** Team conversion rate is below acceptable threshold. Schedule training workshops on objection handling and closing techniques.")
    elif avg_conv < 75:
        insights['recommendations'].append("📈 **ACTION NEEDED:** Conversion rate has room for improvement. Consider role-playing exercises and peer learning sessions.")
    else:
        insights['recommendations'].append("✅ **EXCELLENT:** Team is performing above target. Document and replicate successful strategies across the team.")
    
    # Check individual performers
    low_performers = df[df['conversion'] < 60]
    if len(low_performers) > 0:
        names = ', '.join(low_performers['name'].tolist())
        insights['recommendations'].append(f"🎯 **PRIORITY SUPPORT:** These team members need immediate coaching: {names}. Assign mentors and create personalized improvement plans.")
    
    # Check pitch achievement
    avg_pitch = insights['avg_pitch_achievement']
    if avg_pitch < 70:
        insights['recommendations'].append("📞 **ACTIVITY ALERT:** Pitch activity is significantly below target (<70%). Review daily schedules, increase call blocks, and monitor real-time progress.")
    elif avg_pitch < 85:
        insights['recommendations'].append("📊 **VOLUME CHECK:** Pitch completion needs improvement. Set daily mini-targets and celebrate small wins to boost momentum.")
    
    # Check registration achievement
    avg_reg = insights['avg_reg_achievement']
    if avg_reg < 70:
        insights['recommendations'].append("🎯 **CONVERSION FOCUS:** Registration achievement is low. Review follow-up processes, strengthen closing techniques, and reduce time-to-close.")
    
    # Performance spread analysis
    conversion_spread = df['conversion'].max() - df['conversion'].min()
    if conversion_spread > 30:
        insights['recommendations'].append(f"📊 **CONSISTENCY GAP:** Large performance variance detected ({conversion_spread:.1f}% spread). Standardize processes and share best practices from top performers.")
    
    return insights

# ============================================
# EMAIL REPORTING FUNCTION
# ============================================

def send_email_report(recipient_emails, subject, df, insights):
    """Send comprehensive email report with performance data"""
    
    # Check email configuration
    if not all([
        "email_sender" in st.secrets,
        "email_password" in st.secrets,
        "email_smtp_server" in st.secrets,
        "email_smtp_port" in st.secrets
    ]):
        return False, "Email configuration not found in secrets.toml"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = st.secrets["email_sender"]
        msg['To'] = ', '.join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
        msg['Subject'] = subject
        
        # Create comprehensive HTML email
        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #F5E6D3;
                }}
                .container {{
                    max-width: 800px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                .header {{
                    background: linear-gradient(135deg, #E63946 0%, #D62828 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5rem;
                    letter-spacing: 3px;
                    font-weight: 900;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.1rem;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .metric {{
                    background: #F5E6D3;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #E63946;
                    border-radius: 5px;
                }}
                .metric strong {{
                    color: #1A1A1A;
                    font-size: 1.1rem;
                }}
                .insight {{
                    background: #d4edda;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #2A9D8F;
                    border-radius: 5px;
                }}
                .warning {{
                    background: #fff3cd;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 5px solid #F77F00;
                    border-radius: 5px;
                }}
                .section-title {{
                    color: #1A1A1A;
                    font-size: 1.5rem;
                    font-weight: 900;
                    margin: 30px 0 15px 0;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #E63946;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    background: white;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                }}
                th {{
                    background: #1A1A1A;
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                tr:hover {{
                    background-color: #F5E6D3;
                }}
                .footer {{
                    background: #1A1A1A;
                    color: white;
                    text-align: center;
                    padding: 30px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                .highlight {{
                    background: #E63946;
                    color: white;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-weight: 700;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>IRON LADY</h1>
                    <p>Sales Performance Report - {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="content">
                    <h2 class="section-title">📊 Executive Summary</h2>
                    <div class="metric">
                        <strong>Total Team Size:</strong> {insights['total_rms']} RMs<br/>
                        <strong>Total Pitches:</strong> {insights['total_pitches']}<br/>
                        <strong>Total Registrations:</strong> {insights['total_registrations']}<br/>
                        <strong>Team Average Conversion:</strong> <span class="highlight">{insights['avg_conversion']}%</span>
                    </div>
                    
                    <div class="metric">
                        <strong>Average Pitch Achievement:</strong> {insights['avg_pitch_achievement']}%<br/>
                        <strong>Average Registration Achievement:</strong> {insights['avg_reg_achievement']}%
                    </div>
        """
        
        # Add best performer section
        if insights['best_performer']:
            html_body += f"""
                    <h2 class="section-title">⭐ Top Performer</h2>
                    <div class="insight">
                        <strong>🏆 Name:</strong> {insights['best_performer']['name']}<br/>
                        <strong>📈 Conversion Rate:</strong> <span class="highlight">{insights['best_performer']['conversion']}%</span><br/>
                        <strong>💼 Pitches:</strong> {insights['best_performer']['pitches']}<br/>
                        <strong>✅ Registrations:</strong> {insights['best_performer']['registrations']}<br/>
                        <strong>🎯 Status:</strong> Outstanding Performance - Use as team benchmark
                    </div>
            """
        
        # Add needs support section
        if insights['needs_support']:
            html_body += f"""
                    <h2 class="section-title">📉 Requires Attention</h2>
                    <div class="warning">
                        <strong>👤 Name:</strong> {insights['needs_support']['name']}<br/>
                        <strong>📊 Conversion Rate:</strong> {insights['needs_support']['conversion']}%<br/>
                        <strong>💼 Pitches:</strong> {insights['needs_support']['pitches']}<br/>
                        <strong>✅ Registrations:</strong> {insights['needs_support']['registrations']}<br/>
                        <strong>🎯 Action:</strong> Provide immediate coaching and support
                    </div>
            """
        
        # Add recommendations
        html_body += '<h2 class="section-title">💡 Strategic Recommendations</h2>'
        for idx, rec in enumerate(insights['recommendations'], 1):
            html_body += f'<div class="warning"><strong>#{idx}:</strong> {rec}</div>'
        
        # Add team performance table
        html_body += """
                    <h2 class="section-title">👥 Team Performance Breakdown</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Team Leader</th>
                                <th>RMs</th>
                                <th>Pitches</th>
                                <th>Pitch %</th>
                                <th>Registrations</th>
                                <th>Reg %</th>
                                <th>Conversion</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for _, row in df.iterrows():
            conv_color = '#2A9D8F' if row['conversion'] >= 75 else '#F77F00' if row['conversion'] >= 60 else '#D62828'
            html_body += f"""
                            <tr>
                                <td><strong>{row['name']}</strong></td>
                                <td>{row['rms']}</td>
                                <td>{row['pitches_actual']}/{row['pitches_target']}</td>
                                <td>{row['pitch_achievement']}%</td>
                                <td>{row['reg_actual']}/{row['reg_target']}</td>
                                <td>{row['reg_achievement']}%</td>
                                <td style="color: {conv_color}; font-weight: 700;">{row['conversion']}%</td>
                            </tr>
            """
        
        html_body += """
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    <p style="font-size: 1.3rem; font-weight: 900; margin-bottom: 10px;">IRON LADY</p>
                    <p>Sales Performance Management System</p>
                    <p style="margin-top: 15px;">Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
                    <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">
                        © 2024 Iron Lady. All rights reserved.<br/>
                        This is an automated report. For questions, contact your team leader.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(st.secrets["email_smtp_server"], int(st.secrets["email_smtp_port"]))
        server.starttls()
        server.login(st.secrets["email_sender"], st.secrets["email_password"])
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, f"Error: {str(e)}\n\nDetails:\n{error_details}"

# ============================================
# SAMPLE DATA (FALLBACK)
# ============================================

def get_sample_data():
    """Sample data for demo/fallback"""
    return [
        {
            'name': 'Ghazala',
            'rms': 5,
            'leads': 50,
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
            'leads': 40,
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
            'leads': 30,
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
            'leads': 28,
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
# MAIN DASHBOARD
# ============================================

def main():
    # ============================================
    # HEADER
    # ============================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, {IRONLADY_COLORS['accent']} 0%, white 100%); border-radius: 15px; border: 4px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
            <h1 style="font-size: 3.5rem; margin: 0; letter-spacing: 5px; text-transform: uppercase;">IRON LADY</h1>
            <p style="font-size: 1.3rem; margin: 10px 0 0 0; font-weight: 600;">Sales Performance Dashboard</p>
            <p style="font-size: 0.9rem; margin: 5px 0 0 0; opacity: 0.7;">Real-time Analytics & AI Insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.markdown("### ⚙️ DASHBOARD SETTINGS")
        
        st.markdown("---")
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox("📈 Use Google Sheets", value=True)
        
        sheet_id = None
        if use_sheets:
            if "google_sheet_id" in st.secrets:
                sheet_id = st.secrets["google_sheet_id"]
                st.success("✅ Sheet ID configured")
            else:
                sheet_id = st.text_input(
                    "Google Sheet ID or URL",
                    placeholder="1abc123xyz... or full URL",
                    help="Paste your Google Sheet ID or complete URL"
                )
        
        st.markdown("---")
        
        # Refresh controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("Auto 5min", value=False)
        
        st.markdown(f"**🕐 Last Updated**")
        st.markdown(f"{datetime.now().strftime('%I:%M %p')}")
        
        st.markdown("---")
        st.markdown("### 👥 TEAM LEADERS")
        for idx, tl in enumerate(TEAM_LEADERS, 1):
            icon = "🏆" if tl in ['Ghazala', 'Megha'] else "🌟"
            st.markdown(f"{icon} **{tl}**")
        
        st.markdown("---")
        st.markdown("### 📧 QUICK ACTIONS")
        if st.button("📨 Send Report", use_container_width=True, type="primary"):
            st.info("👆 Go to 'Email Report' tab to send")
    
    # ============================================
    # FETCH AND PROCESS DATA
    # ============================================
    team_data = None
    data_source = "Sample Data (Demo Mode)"
    
    if use_sheets and sheet_id:
        with st.spinner("📊 Loading data from Google Sheets..."):
            sheet_data = fetch_sheet_data(sheet_id)
            if sheet_data:
                team_data = parse_team_data(sheet_data)
                if team_data:
                    data_source = "🟢 Google Sheets (Live Data)"
                    st.success("✅ Live data loaded successfully!")
    
    # Fallback to sample data
    if not team_data:
        team_data = get_sample_data()
        if use_sheets:
            st.warning("⚠️ Using sample data. Check your Google Sheets connection.")
    
    # Convert to DataFrame
    df = pd.DataFrame(team_data)
    
    # Calculate overall metrics
    total_rms = int(df['rms'].sum())
    total_leads = int(df.get('leads', pd.Series([0])).sum())
    total_pitch_target = int(df['pitches_target'].sum())
    total_pitch_actual = int(df['pitches_actual'].sum())
    total_reg_target = int(df['reg_target'].sum())
    total_reg_actual = int(df['reg_actual'].sum())
    
    overall_pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
    overall_reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
    overall_conversion = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
    
    # Data Source Badge
    badge_color = '#d4edda' if 'Live' in data_source else '#fff3cd'
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: {badge_color}; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <strong style="font-size: 1.1rem;">📊 Data Source:</strong> {data_source}<br/>
        <strong style="font-size: 0.95rem;">🕐 Updated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # MAIN TABS
    # ============================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Performance Dashboard",
        "🤖 AI Analysis & Insights",
        "📧 Email Reports",
        "📋 Data View"
    ])
    
    # ============================================
    # TAB 1: PERFORMANCE DASHBOARD
    # ============================================
    with tab1:
        st.markdown("### 📊 OVERALL TEAM PERFORMANCE")
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="👥 Total RMs",
                value=total_rms,
                delta=None
            )
        
        with col2:
            st.metric(
                label="📞 Total Leads",
                value=total_leads if total_leads > 0 else "N/A",
                delta=None
            )
        
        with col3:
            pitch_delta = f"+{overall_pitch_achievement - 100:.1f}%" if overall_pitch_achievement >= 100 else f"{overall_pitch_achievement - 100:.1f}%"
            st.metric(
                label="🎯 Pitch Achievement",
                value=f"{overall_pitch_achievement}%",
                delta=pitch_delta
            )
        
        with col4:
            reg_delta = f"+{overall_reg_achievement - 100:.1f}%" if overall_reg_achievement >= 100 else f"{overall_reg_achievement - 100:.1f}%"
            st.metric(
                label="📝 Reg Achievement",
                value=f"{overall_reg_achievement}%",
                delta=reg_delta
            )
        
        with col5:
            conv_status = "Excellent" if overall_conversion >= 75 else "Good" if overall_conversion >= 60 else "Needs Work"
            st.metric(
                label="💯 Conversion Rate",
                value=f"{overall_conversion}%",
                delta=conv_status
            )
        
        st.markdown("---")
        
        # Detailed Progress
        st.markdown("### 📈 DETAILED PROGRESS")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Pitch Progress")
            st.markdown(f"""
            <div class="metric">
                <strong>Target:</strong> {total_pitch_target} pitches<br/>
                <strong>Actual:</strong> {total_pitch_actual} pitches<br/>
                <strong>Achievement:</strong> <span style="color: {'#2A9D8F' if overall_pitch_achievement >= 80 else '#F77F00'}; font-weight: 700;">{overall_pitch_achievement}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📝 Registration Progress")
            st.markdown(f"""
            <div class="metric">
                <strong>Target:</strong> {total_reg_target} registrations<br/>
                <strong>Actual:</strong> {total_reg_actual} registrations<br/>
                <strong>Achievement:</strong> <span style="color: {'#2A9D8F' if overall_reg_achievement >= 80 else '#F77F00'}; font-weight: 700;">{overall_reg_achievement}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Team Leader Performance Table
        st.markdown("### 👥 TEAM LEADER PERFORMANCE")
        
        display_df = df.copy()
        display_df['Pitch Progress'] = display_df.apply(
            lambda x: f"{x['pitches_actual']}/{x['pitches_target']} ({x['pitch_achievement']}%)", axis=1
        )
        display_df['Reg Progress'] = display_df.apply(
            lambda x: f"{x['reg_actual']}/{x['reg_target']} ({x['reg_achievement']}%)", axis=1
        )
        display_df['Conversion'] = display_df['conversion'].apply(lambda x: f"{x}%")
        
        table_df = display_df[['name', 'rms', 'Pitch Progress', 'Reg Progress', 'Conversion']]
        table_df.columns = ['Team Leader', 'RMs', 'Pitches', 'Registrations', 'Conversion Rate']
        
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=250
        )
        
        st.markdown("---")
        
        # Visualizations
        st.markdown("### 📊 PERFORMANCE VISUALIZATIONS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💯 Conversion Rate Comparison")
            fig1 = px.bar(
                df,
                x='name',
                y='conversion',
                color='conversion',
                color_continuous_scale=['#D62828', '#F77F00', '#2A9D8F'],
                labels={'name': 'Team Leader', 'conversion': 'Conversion Rate (%)'},
                text='conversion'
            )
            fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig1.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="",
                yaxis_title="Conversion Rate (%)"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Achievement Comparison")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Pitch Achievement',
                x=df['name'],
                y=df['pitch_achievement'],
                marker_color=IRONLADY_COLORS['success'],
                text=df['pitch_achievement'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside'
            ))
            fig2.add_trace(go.Bar(
                name='Registration Achievement',
                x=df['name'],
                y=df['reg_achievement'],
                marker_color=IRONLADY_COLORS['warning'],
                text=df['reg_achievement'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside'
            ))
            fig2.update_layout(
                barmode='group',
                height=400,
                xaxis_title="",
                yaxis_title='Achievement (%)',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Pie Chart - Team Contribution
        st.markdown("#### 🥧 Team Contribution to Total Registrations")
        fig3 = px.pie(
            df,
            values='reg_actual',
            names='name',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    # ============================================
    # TAB 2: AI ANALYSIS
    # ============================================
    with tab2:
        st.markdown("### 🤖 AI-POWERED PERFORMANCE ANALYSIS")
        
        st.markdown("""
        <div class="info-msg">
            🔍 <strong>Advanced Analytics Engine</strong><br/>
            Our AI analyzes team performance patterns, identifies trends, and generates actionable insights automatically.
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("🧠 Analyzing team performance data..."):
            insights = analyze_team_performance(df)
        
        # Executive Summary
        st.markdown("### 📊 EXECUTIVE SUMMARY")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Team Size", f"{insights['total_rms']} RMs")
        
        with col2:
            st.metric("📞 Total Pitches", insights['total_pitches'])
        
        with col3:
            st.metric("📝 Total Registrations", insights['total_registrations'])
        
        with col4:
            conv_color = "🟢" if insights['avg_conversion'] >= 75 else "🟡" if insights['avg_conversion'] >= 60 else "🔴"
            st.metric("💯 Avg Conversion", f"{conv_color} {insights['avg_conversion']}%")
        
        st.markdown("---")
        
        # Performance Status
        st.markdown("### 🎯 OVERALL PERFORMANCE STATUS")
        
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
            <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Team Average: {insights['avg_conversion']}% | Pitch: {insights['avg_pitch_achievement']}% | Reg: {insights['avg_reg_achievement']}%</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                    <strong>Pitches:</strong> {bp['pitches']}<br/>
                    <strong>Registrations:</strong> {bp['registrations']}<br/>
                    <strong>Status:</strong> Outstanding Performance<br/>
                    <strong>Action:</strong> Document best practices and share with team
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
                    <strong>Pitches:</strong> {ns['pitches']}<br/>
                    <strong>Registrations:</strong> {ns['registrations']}<br/>
                    <strong>Status:</strong> Requires Attention<br/>
                    <strong>Action:</strong> Provide coaching and mentorship
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # AI Recommendations
        st.markdown("### 💡 STRATEGIC RECOMMENDATIONS")
        st.markdown("""
        <div class="info-msg">
            📋 <strong>AI-Generated Action Items</strong><br/>
            Based on current performance data and historical trends
        </div>
        """, unsafe_allow_html=True)
        
        for idx, rec in enumerate(insights['recommendations'], 1):
            st.markdown(f"""
            <div class="insight-box">
                <strong>Recommendation #{idx}:</strong><br/>
                {rec}
            </div>
            """, unsafe_allow_html=True)
        
        # Performance Distribution
        st.markdown("---")
        st.markdown("### 📊 PERFORMANCE DISTRIBUTION")
        
        fig4 = go.Figure()
        fig4.add_trace(go.Box(
            y=df['conversion'],
            name='Conversion Rate',
            marker_color=IRONLADY_COLORS['primary'],
            boxmean='sd'
        ))
        fig4.update_layout(
            title='Team Conversion Rate Distribution',
            yaxis_title='Conversion Rate (%)',
            height=400
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # ============================================
    # TAB 3: EMAIL REPORTS
    # ============================================
    with tab3:
        st.markdown("### 📧 AUTOMATED EMAIL REPORTING")
        
        st.markdown("""
        <div class="info-msg">
            📨 <strong>Professional Email Reports</strong><br/>
            Send comprehensive performance reports with AI insights to multiple recipients instantly.
        </div>
        """, unsafe_allow_html=True)
        
        # Email configuration check
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
                Add email settings to your <code>.streamlit/secrets.toml</code> file to enable this feature.
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📋 Email Configuration Guide"):
                st.markdown("""
                Add these lines to `.streamlit/secrets.toml`:
                
                ```toml
                email_sender = "your-email@gmail.com"
                email_password = "your-app-password"
                email_smtp_server = "smtp.gmail.com"
                email_smtp_port = "587"
                ```
                
                **For Gmail:**
                1. Enable 2-factor authentication in Google Account
                2. Go to Security → App passwords
                3. Generate a new app password for "Mail"
                4. Use that 16-character password (not your regular password)
                
                **For Other Providers:**
                - Outlook/Hotmail: smtp.office365.com, port 587
                - Yahoo: smtp.mail.yahoo.com, port 587
                """)
        else:
            st.markdown("""
            <div class="success-msg">
                ✅ <strong>Email Configured</strong><br/>
                Ready to send professional reports with AI insights and performance data.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Email form
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📬 Recipients")
            recipient_emails = st.text_area(
                "Email Addresses",
                placeholder="manager@company.com\nteamlead@company.com\nsupervisor@company.com",
                height=150,
                help="Enter multiple emails separated by commas or new lines"
            )
            
            st.markdown("#### 📝 Subject Line")
            subject = st.text_input(
                "Email Subject",
                value=f"Iron Lady Sales Report - {datetime.now().strftime('%B %d, %Y')}",
                help="Customize the email subject line"
            )
        
        with col2:
            st.markdown("#### 📊 Preview")
            st.markdown(f"""
            <div class="metric">
                <strong>Report Includes:</strong><br/>
                ✅ Team Summary<br/>
                ✅ Individual Performance<br/>
                ✅ AI Insights<br/>
                ✅ Recommendations<br/>
                ✅ Top Performers<br/>
                ✅ Action Items
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Send button
            if st.button("📧 SEND EMAIL REPORT", use_container_width=True, type="primary", disabled=not email_configured):
                if recipient_emails:
                    # Parse emails
                    emails = [e.strip() for e in recipient_emails.replace(',', '\n').split('\n') if e.strip()]
                    
                    if emails:
                        with st.spinner("📤 Generating and sending email report..."):
                            # Generate insights
                            insights = analyze_team_performance(df)
                            
                            # Send email
                            success, message = send_email_report(
                                emails,
                                subject,
                                df,
                                insights
                            )
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.success(f"📧 Report sent to {len(emails)} recipient(s)!")
                                st.balloons()
                                
                                # Show recipient list
                                st.markdown("**Recipients:**")
                                for email in emails:
                                    st.markdown(f"- {email}")
                            else:
                                st.error(f"❌ Failed to send email")
                                st.error(message)
                    else:
                        st.error("❌ Please enter at least one valid email address")
                else:
                    st.error("❌ Please enter recipient email addresses")
        
        st.markdown("---")
        
        # Email preview
        with st.expander("👁️ Preview Email Content"):
            st.markdown("""
            The email report includes:
            - **Executive Summary**: Overall team metrics and performance
            - **Top Performer Spotlight**: Best performing team member
            - **Support Needed**: Team members requiring coaching
            - **AI Recommendations**: Strategic action items
            - **Detailed Table**: Complete team performance breakdown
            - **Professional Branding**: Iron Lady theme with team leaders
            """)
    
    # ============================================
    # TAB 4: DATA VIEW
    # ============================================
    with tab4:
        st.markdown("### 📋 RAW DATA VIEW")
        
        st.markdown("""
        <div class="info-msg">
            📊 <strong>Complete Dataset</strong><br/>
            View and download all performance data in table format
        </div>
        """, unsafe_allow_html=True)
        
        # Display full dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("---")
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"iron_lady_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"iron_lady_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        # Data statistics
        st.markdown("---")
        st.markdown("### 📈 DATA STATISTICS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Metrics Summary**")
            st.write(df[['rms', 'pitches_actual', 'reg_actual', 'conversion']].describe())
        
        with col2:
            st.markdown("**🏆 Top Metrics**")
            st.write(f"**Highest Conversion:** {df['conversion'].max()}%")
            st.write(f"**Most RMs:** {df['rms'].max()}")
            st.write(f"**Most Pitches:** {df['pitches_actual'].max()}")
            st.write(f"**Most Registrations:** {df['reg_actual'].max()}")
        
        with col3:
            st.markdown("**📉 Performance Gaps**")
            st.write(f"**Conversion Spread:** {df['conversion'].max() - df['conversion'].min():.1f}%")
            st.write(f"**Pitch Gap:** {df['pitch_achievement'].max() - df['pitch_achievement'].min():.1f}%")
            st.write(f"**Reg Gap:** {df['reg_achievement'].max() - df['reg_achievement'].min():.1f}%")
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {IRONLADY_COLORS['secondary']} 0%, {IRONLADY_COLORS['primary']} 100%); border-radius: 15px; color: white; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
        <p style="margin: 0; font-weight: 900; font-size: 1.5rem; letter-spacing: 2px;">IRON LADY</p>
        <p style="margin: 10px 0 0 0; font-size: 1rem;">Sales Performance Management System</p>
        <p style="margin: 10px 0 0 0; font-size: 0.95rem;">Complete Edition with AI Analysis & Email Reports</p>
        <p style="margin: 15px 0 0 0; font-size: 0.9rem; opacity: 0.9;">Team Leaders: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
        <p style="margin: 15px 0 0 0; font-size: 0.85rem; opacity: 0.7;">© 2024 Iron Lady. All rights reserved. | v9.0 Complete</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
