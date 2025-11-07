"""
IRON LADY - COMPLETE SALES DASHBOARD WITH OCR/NER
==================================================
ALL FEATURES IN ONE FILE:
- Multi-user Login System (4 Team Leaders)
- Individual Dashboards with Manual Data Entry
- Google Sheets Integration (AUTO-LOADS BY DEFAULT)
- Performance Dashboard with Interactive Charts
- AI-Powered Analysis & Insights
- Email Reports to Multiple Recipients
- Daily Checklists (Day 1-1, Day 1, Day 2)
- OCR (Text Extraction from Screenshots)
- NER (Named Entity Recognition)
- Automatic Metric Detection
- Complete Session Management

Team: Ghazala (Senior TL), Megha (Senior TL), Afreen (Trainee TL), Soumya (Trainee TL)
Version: 12.0 - Complete OCR/NER Edition
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
from PIL import Image
import re

# Try to import OCR/NER libraries
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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
    'info': '#457B9D'
}

# Custom CSS with FIXED text visibility
st.markdown(f"""
<style>
    /* Main theme colors */
    :root {{
        --primary-color: {IRONLADY_COLORS['primary']};
        --secondary-color: {IRONLADY_COLORS['secondary']};
        --accent-color: {IRONLADY_COLORS['accent']};
    }}
    
    /* CRITICAL FIX: Ensure all text is visible */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{
        color: {IRONLADY_COLORS['secondary']} !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4 {{
        color: {IRONLADY_COLORS['secondary']} !important;
        font-weight: 900 !important;
    }}
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {IRONLADY_COLORS['secondary']} 0%, {IRONLADY_COLORS['primary']} 100%);
    }}
    
    .css-1d391kg p, [data-testid="stSidebar"] p,
    .css-1d391kg span, [data-testid="stSidebar"] span,
    .css-1d391kg label, [data-testid="stSidebar"] label {{
        color: white !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {IRONLADY_COLORS['primary']} !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {IRONLADY_COLORS['secondary']} !important;
        font-weight: 700 !important;
    }}
    
    /* Buttons */
    .stButton>button {{
        background: {IRONLADY_COLORS['primary']};
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background: {IRONLADY_COLORS['secondary']};
    }}
    
    /* Info boxes */
    .info-msg {{
        background: {IRONLADY_COLORS['accent']};
        padding: 1rem;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        margin: 1rem 0;
        color: {IRONLADY_COLORS['secondary']} !important;
    }}
    
    .success-msg {{
        background: #d4edda;
        padding: 1rem;
        border-left: 5px solid {IRONLADY_COLORS['success']};
        margin: 1rem 0;
        color: #155724 !important;
    }}
    
    .warning-msg {{
        background: #fff3cd;
        padding: 1rem;
        border-left: 5px solid {IRONLADY_COLORS['warning']};
        margin: 1rem 0;
        color: #856404 !important;
    }}
    
    /* Tables */
    .dataframe {{
        color: {IRONLADY_COLORS['secondary']} !important;
    }}
    
    .dataframe th {{
        background: {IRONLADY_COLORS['secondary']} !important;
        color: white !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {{
        color: {IRONLADY_COLORS['secondary']};
        font-weight: 700;
    }}
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {IRONLADY_COLORS['primary']};
        border-bottom: 3px solid {IRONLADY_COLORS['primary']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'team_data' not in st.session_state:
    st.session_state.team_data = {}

if 'sheets_data_loaded' not in st.session_state:
    st.session_state.sheets_data_loaded = False

if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = {}

if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = {}

if 'checklist_state' not in st.session_state:
    st.session_state.checklist_state = {}

# ============================================
# USER CREDENTIALS
# ============================================

USERS = {
    'ghazala': {
        'password': 'ironlady2024',
        'name': 'Ghazala',
        'role': 'Senior Team Leader',
        'team_size': 7
    },
    'megha': {
        'password': 'ironlady2024',
        'name': 'Megha',
        'role': 'Senior Team Leader',
        'team_size': 7
    },
    'afreen': {
        'password': 'ironlady2024',
        'name': 'Afreen',
        'role': 'Trainee Team Leader',
        'team_size': 5
    },
    'soumya': {
        'password': 'ironlady2024',
        'name': 'Soumya',
        'role': 'Trainee Team Leader',
        'team_size': 6
    }
}

# ============================================
# DAILY CHECKLISTS
# ============================================

DAILY_CHECKLISTS = {
    'Day 1-1': {
        'tasks': [
            {'name': 'Mocks - Who are the people - Buddy structure', 'priority': 'high', 'type': 'manual'},
            {'name': 'Sign off Activities - each RM type', 'priority': 'high', 'type': 'manual'},
            {'name': 'WA Audit - Minimum 10', 'priority': 'high', 'type': 'upload'},
            {'name': 'Follow up Calls - 2 Registrations', 'priority': 'high', 'type': 'manual'},
            {'name': 'SL Calls - 5 (Share status list)', 'priority': 'high', 'type': 'upload'},
            {'name': 'Lead Analysis AI summary', 'priority': 'medium', 'type': 'manual'},
            {'name': 'Call Audit - Minimum 5 calls', 'priority': 'high', 'type': 'upload'},
            {'name': 'Tracking: CRM Update, Call/Attendance/WA', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Targets Sharing - percentage and potential list', 'priority': 'medium', 'type': 'manual'},
            {'name': 'CRM Updation', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Sharing hot prospects list', 'priority': 'medium', 'type': 'manual'},
        ]
    },
    'Day 1': {
        'tasks': [
            {'name': 'WA Audit - 10', 'priority': 'high', 'type': 'upload'},
            {'name': 'SL Calls - 8 (Share status list)', 'priority': 'high', 'type': 'upload'},
            {'name': 'Sign off Activities', 'priority': 'high', 'type': 'manual'},
            {'name': 'Mocks - Buddy structure', 'priority': 'high', 'type': 'manual'},
            {'name': '30s pitch Prep', 'priority': 'medium', 'type': 'manual'},
            {'name': 'Tracking: CRM Update', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Call Audit - Minimum 5 calls', 'priority': 'high', 'type': 'upload'},
            {'name': 'Targets Sharing - % and potential list', 'priority': 'medium', 'type': 'manual'},
            {'name': '10% Conversion - action points', 'priority': 'high', 'type': 'manual'},
            {'name': 'CRM Updation - including attendance', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Sharing hot prospects list and Tracking', 'priority': 'medium', 'type': 'manual'},
        ]
    },
    'Day 2': {
        'tasks': [
            {'name': 'SL Calls - 10-12 (Share status list)', 'priority': 'high', 'type': 'upload'},
            {'name': 'WA Audit - As needed', 'priority': 'medium', 'type': 'upload'},
            {'name': 'Tracking: CRM Update', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Sign off Activities', 'priority': 'high', 'type': 'manual'},
            {'name': 'Targets Sharing - 10% before, 15% after', 'priority': 'high', 'type': 'manual'},
            {'name': 'CRM Updation - including attendance', 'priority': 'high', 'type': 'ongoing'},
            {'name': 'Sharing hot prospects list and Tracking', 'priority': 'medium', 'type': 'manual'},
        ]
    }
}

# ============================================
# OCR FUNCTIONS
# ============================================

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    if not CV2_AVAILABLE:
        return image
    
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Noise removal
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return Image.fromarray(denoised)
    except Exception as e:
        return image

def extract_text_from_image(image):
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        return None, "OCR not available. Install pytesseract."
    
    try:
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Extract text
        text = pytesseract.image_to_string(processed_image)
        
        return text, None
    except Exception as e:
        return None, f"OCR Error: {str(e)}"

# ============================================
# NER FUNCTIONS
# ============================================

def extract_entities(text):
    """Extract named entities from text"""
    if not NER_AVAILABLE:
        return None, "NER not available"
    
    try:
        doc = nlp(text)
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'DATE': [],
            'MONEY': [],
            'CARDINAL': [],
            'PERCENT': [],
            'PHONE': [],
            'EMAIL': []
        }
        
        # Extract spaCy entities
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Extract phone numbers (simple regex)
        phones = re.findall(r'\b\d{10}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        entities['PHONE'] = phones
        
        # Extract emails (simple regex)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        entities['EMAIL'] = emails
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities, None
    except Exception as e:
        return None, f"NER Error: {str(e)}"

def extract_metrics_from_text(text):
    """Extract sales metrics from text"""
    metrics = {
        'pitches': [],
        'registrations': [],
        'leads': [],
        'rms': []
    }
    
    # Look for numbers near keywords
    patterns = {
        'pitches': r'(?:pitch|pitches|calls?)\s*[:=]?\s*(\d+)',
        'registrations': r'(?:registration|registrations|reg|regs)\s*[:=]?\s*(\d+)',
        'leads': r'(?:lead|leads)\s*[:=]?\s*(\d+)',
        'rms': r'(?:rm|rms|team\s*member)\s*[:=]?\s*(\d+)'
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics[key] = [int(m) for m in matches]
    
    return metrics

# ============================================
# GOOGLE SHEETS INTEGRATION
# ============================================

def parse_team_sheet(worksheet):
    """Parse a team leader's worksheet with complex structure"""
    try:
        all_data = worksheet.get_all_values()
        
        # Find the team leader name from the sheet
        team_name = None
        for row in all_data[:10]:
            if row[1] and ('-' in row[1] or 'Rising' in row[1] or 'Winners' in row[1] or 'Flyers' in row[1] or 'Getters' in row[1]):
                team_name = row[1]
                break
        
        # Initialize aggregates
        total_wa_audit = 0
        total_call_audit = 0
        total_mocks = 0
        total_sl_calls = 0
        total_registrations = 0
        total_pitches = 0
        total_current_mc = 0
        rm_count = 0
        
        # Parse each row looking for achieved values
        for row in all_data:
            if len(row) < 15:
                continue
            
            # Check if this is a data row (has RM name and numbers)
            rm_name = row[1] if len(row) > 1 else ''
            
            # Skip header rows and team name rows
            if not rm_name or 'RM Name' in rm_name or 'Target' in rm_name or 'Achieved' in rm_name:
                continue
            if team_name and team_name in rm_name:
                continue
            
            # Try to extract achieved values from various columns
            try:
                # WA Audit Achieved (column D, index 3)
                if len(row) > 3 and row[3] and row[3].strip() and row[3].strip().isdigit():
                    total_wa_audit += int(row[3])
                
                # Call Audit Achieved (column F, index 5)
                if len(row) > 5 and row[5] and row[5].strip() and row[5].strip().isdigit():
                    total_call_audit += int(row[5])
                
                # Mocks Achieved (column H, index 7)
                if len(row) > 7 and row[7] and row[7].strip() and row[7].strip().isdigit():
                    total_mocks += int(row[7])
                
                # SL Calls Achieved (column J, index 9)
                if len(row) > 9 and row[9] and row[9].strip() and row[9].strip().isdigit():
                    total_sl_calls += int(row[9])
                
                # Follow ups Registrations Achieved (column L, index 11)
                if len(row) > 11 and row[11] and row[11].strip():
                    val = row[11].strip()
                    # Extract number even if it has text (like "1-Shwetha")
                    num = re.findall(r'\d+', val)
                    if num:
                        total_registrations += int(num[0])
                
                # Pitches Achieved (column N, index 13)
                if len(row) > 13 and row[13] and row[13].strip() and row[13].strip().isdigit():
                    total_pitches += int(row[13])
                
                # Current MC Registrations Achieved (column P, index 15)
                if len(row) > 15 and row[15] and row[15].strip() and row[15].strip().isdigit():
                    total_current_mc += int(row[15])
                
                # Count this RM if they have any data
                if any([row[3], row[5], row[7], row[9], row[11], row[13], row[15]]):
                    rm_count += 1
            except:
                continue
        
        # Calculate conversion rate
        conversion_rate = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0.0
        
        return {
            'team_name': team_name,
            'total_rms': rm_count,
            'total_wa_audit': total_wa_audit,
            'total_call_audit': total_call_audit,
            'total_mocks': total_mocks,
            'total_sl_calls': total_sl_calls,
            'total_pitches': total_pitches,
            'total_registrations': total_registrations,
            'total_current_mc': total_current_mc,
            'conversion_rate': conversion_rate
        }
    
    except Exception as e:
        st.error(f"Error parsing sheet: {e}")
        return None

def load_from_sheets():
    """Load data from Google Sheets with multiple team sheets"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Try to get credentials from Streamlit secrets
        if 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets:
            credentials_dict = dict(st.secrets['GOOGLE_SHEETS_CREDENTIALS'])
            sheet_id = st.secrets.get('GOOGLE_SHEET_ID', '')
            
            if sheet_id:
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets.readonly',
                        'https://www.googleapis.com/auth/drive.readonly'
                    ]
                )
                
                client = gspread.authorize(credentials)
                spreadsheet = client.open_by_key(sheet_id)
                
                # Get all worksheets
                worksheets = spreadsheet.worksheets()
                
                # Map worksheet names to team leaders
                sheet_mapping = {
                    'Ghazala': 'ghazala',
                    'Megha': 'megha',
                    'Afreen': 'afreen',
                    'Soumya': 'soumya'
                }
                
                loaded_count = 0
                
                # Parse each team leader's sheet
                for worksheet in worksheets:
                    sheet_title = worksheet.title
                    
                    # Find matching team leader
                    username = None
                    for sheet_name, user in sheet_mapping.items():
                        if sheet_name.lower() in sheet_title.lower():
                            username = user
                            break
                    
                    if username and username in USERS:
                        # Parse the sheet
                        data = parse_team_sheet(worksheet)
                        
                        if data:
                            # Store in session state
                            st.session_state.team_data[username] = data
                            loaded_count += 1
                
                if loaded_count > 0:
                    st.session_state.sheets_data_loaded = True
                    return True, f"Data loaded from {loaded_count} team sheets successfully!"
                else:
                    return False, "No data found in sheets"
        
        return False, "Google Sheets not configured"
    
    except Exception as e:
        return False, f"Error loading from Google Sheets: {str(e)}"

# ============================================
# LOGIN SYSTEM
# ============================================

def show_login():
    """Display login page"""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, {IRONLADY_COLORS['primary']} 0%, {IRONLADY_COLORS['secondary']} 100%); border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; font-size: 3rem; font-weight: 900; margin: 0; letter-spacing: 3px;'>IRON LADY</h1>
            <p style='color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;'>Sales Performance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Team Leader Login")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("🚀 LOGIN", use_container_width=True):
            if username.lower() in USERS and USERS[username.lower()]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username.lower()
                
                # Try to load Google Sheets data on login
                success, message = load_from_sheets()
                if success:
                    st.success(message)
                
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.markdown("""
        <div class="info-msg">
            <strong>👥 Team Leaders:</strong><br/>
            • Ghazala (Senior TL)<br/>
            • Megha (Senior TL)<br/>
            • Afreen (Trainee TL)<br/>
            • Soumya (Trainee TL)<br/><br/>
            <strong>Default Password:</strong> ironlady2024
        </div>
        """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

def show_sidebar():
    """Display sidebar with user info and navigation"""
    
    user = st.session_state.current_user
    user_info = USERS[user]
    
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0; font-size: 2rem;'>IRON LADY</h2>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>💪 Sales Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div style='background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
        <p style='color: white; margin: 0; font-size: 0.9rem;'><strong>👤 Name:</strong> {user_info['name']}</p>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;'><strong>🏆 Role:</strong> {user_info['role']}</p>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;'><strong>👥 Team:</strong> {user_info['team_size']} RMs</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.markdown("<p style='color: white; font-weight: 700;'>⚡ QUICK ACTIONS</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 Reload Google Sheets", use_container_width=True):
        with st.spinner("Loading..."):
            success, message = load_from_sheets()
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.info(message)
    
    if st.sidebar.button("📊 Export My Data", use_container_width=True):
        st.sidebar.info("Export feature - Coming soon!")
    
    st.sidebar.markdown("---")
    
    # Logout
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.8rem;'>
        <p>© 2024 Iron Lady<br/>v12.0 - OCR/NER Edition</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 1: MY DASHBOARD
# ============================================

def show_my_dashboard():
    """Show embedded Google Sheet for logged-in user"""
    
    user = st.session_state.current_user
    user_info = USERS[user]
    
    st.markdown(f"# 📊 {user_info['name']}'s Dashboard")
    st.markdown(f"<p style='color: {IRONLADY_COLORS['secondary']}; font-size: 1.1rem;'>{user_info['role']} | Team Size: {user_info['team_size']} RMs</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get sheet ID from secrets
    if 'GOOGLE_SHEET_ID' in st.secrets:
        sheet_id = st.secrets['GOOGLE_SHEET_ID']
        
        # Map username to sheet GID (tab ID)
        # You'll need to find the gid for each sheet tab
        sheet_gids = {
            'ghazala': '0',  # Replace with actual GID for Ghazala tab
            'megha': '1511743141',  # From your screenshot URL
            'afreen': '2077016974',  # From your screenshot URL
            'soumya': '1686874932'  # From your screenshot URL
        }
        
        gid = sheet_gids.get(user, '0')
        
        # Create embed URL
        embed_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}&rm=minimal&single=true&widget=false"
        
        # Display instructions
        st.info("📝 **Tip:** Click on the sheet below to edit directly in Google Sheets. Changes save automatically!")
        
        # Embed the Google Sheet
        st.markdown(
            f'''
            <iframe 
                src="{embed_url}" 
                width="100%" 
                height="800" 
                frameborder="0"
                style="border: 2px solid {IRONLADY_COLORS['primary']}; border-radius: 10px;"
            ></iframe>
            ''',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # Quick link to open in new tab
        full_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}"
        st.markdown(f"[🔗 Open Full Sheet in New Tab]({full_url})")
        
    else:
        st.error("❌ Google Sheet not configured. Please add GOOGLE_SHEET_ID to secrets.")
        st.info("**Temporary workaround:** Use the direct link to your Google Sheet")

# ============================================
# TAB 2: TEAM PERFORMANCE
# ============================================

def show_team_performance():
    """Show all team sheets"""
    
    st.markdown("# 🏆 ALL TEAM SHEETS")
    st.markdown("---")
    
    if 'GOOGLE_SHEET_ID' not in st.secrets:
        st.error("❌ Google Sheet not configured")
        return
    
    sheet_id = st.secrets['GOOGLE_SHEET_ID']
    
    # Team sheets with GIDs
    teams = {
        'Ghazala - Rising Stars': {
            'gid': '0',
            'color': IRONLADY_COLORS['primary']
        },
        'Megha - Winners': {
            'gid': '1511743141',
            'color': IRONLADY_COLORS['success']
        },
        'Afreen - High Flyers': {
            'gid': '2077016974',
            'color': IRONLADY_COLORS['warning']
        },
        'Soumya - Goal Getters': {
            'gid': '1686874932',
            'color': IRONLADY_COLORS['info']
        }
    }
    
    # Create tabs for each team
    tab_names = list(teams.keys())
    tabs = st.tabs(tab_names)
    
    for tab, team_name in zip(tabs, tab_names):
        with tab:
            gid = teams[team_name]['gid']
            embed_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}&rm=minimal&single=true&widget=false"
            full_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?gid={gid}"
            
            st.markdown(f"### {team_name}")
            
            # Embed sheet
            st.markdown(
                f'''
                <iframe 
                    src="{embed_url}" 
                    width="100%" 
                    height="700" 
                    frameborder="0"
                    style="border: 2px solid {teams[team_name]['color']}; border-radius: 10px;"
                ></iframe>
                ''',
                unsafe_allow_html=True
            )
            
            # Link to open in new tab
            st.markdown(f"[🔗 Open in New Tab]({full_url})")
                         barmode='group')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fig4 = px.scatter(df, x='Total Pitches', y='Total Registrations',
                            size='Conversion %', color='Team Leader',
                            title="Pitches vs Registrations (size = conversion %)",
                            hover_data=['Team Name'])
            st.plotly_chart(fig4, use_container_width=True)
    
    else:
        st.info("📝 No team data available yet. Team leaders need to enter their data first or load from Google Sheets!")

# ============================================
# TAB 3: ANALYTICS
# ============================================

def show_analytics():
    """Show advanced analytics"""
    
    st.markdown("# 📈 ADVANCED ANALYTICS")
    st.markdown("---")
    
    team_data_list = []
    for username, user_info in USERS.items():
        if username in st.session_state.team_data:
            data = st.session_state.team_data[username]
            team_data_list.append({
                'Team Leader': user_info['name'],
                'Total Pitches': data.get('total_pitches', 0),
                'Total Registrations': data.get('total_registrations', 0),
                'Conversion %': data.get('conversion_rate', 0),
                'WA Audit': data.get('total_wa_audit', 0),
                'Call Audit': data.get('total_call_audit', 0),
                'SL Calls': data.get('total_sl_calls', 0)
            })
    
    if team_data_list:
        df = pd.DataFrame(team_data_list)
        
        # Performance insights
        st.markdown("### 🎯 PERFORMANCE INSIGHTS")
        
        best_performer = df.loc[df['Conversion %'].idxmax()]
        total_pitches = df['Total Pitches'].sum()
        total_regs = df['Total Registrations'].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="success-msg">
                <h4 style="margin: 0;">🏆 Top Performer</h4>
                <p style="margin: 0.5rem 0 0 0;"><strong>{best_performer['Team Leader']}</strong> with {best_performer['Conversion %']}% conversion rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            target_conversion = 15.0
            current_conversion = round((total_regs / total_pitches * 100), 1) if total_pitches > 0 else 0
            
            if current_conversion >= target_conversion:
                msg_type = "success-msg"
                icon = "✅"
                text = "On Target!"
            else:
                msg_type = "warning-msg"
                icon = "⚠️"
                text = "Below Target"
            
            st.markdown(f"""
            <div class="{msg_type}">
                <h4 style="margin: 0;">{icon} Target Status</h4>
                <p style="margin: 0.5rem 0 0 0;">Current: {current_conversion}% | Target: {target_conversion}% - {text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            most_active = df.loc[df['SL Calls'].idxmax()]
            st.markdown(f"""
            <div class="info-msg">
                <h4 style="margin: 0;">⚡ Most Active</h4>
                <p style="margin: 0.5rem 0 0 0;"><strong>{most_active['Team Leader']}</strong> with {int(most_active['SL Calls'])} SL calls</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Activity efficiency
        st.markdown("### 📊 ACTIVITY EFFICIENCY")
        
        # Calculate efficiency metrics
        df['Audit Efficiency'] = df.apply(
            lambda row: round((row['Total Registrations'] / (row['WA Audit'] + row['Call Audit'])) * 100, 1) 
            if (row['WA Audit'] + row['Call Audit']) > 0 else 0, axis=1
        )
        
        df['Call Efficiency'] = df.apply(
            lambda row: round((row['Total Registrations'] / row['SL Calls']) * 100, 1)
            if row['SL Calls'] > 0 else 0, axis=1
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(df, x='Team Leader', y='Audit Efficiency',
                         title="Audit Efficiency (Regs per 100 Audits)",
                         color='Audit Efficiency',
                         color_continuous_scale='Blues')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(df, x='Team Leader', y='Call Efficiency',
                         title="Call Efficiency (Regs per 100 SL Calls)",
                         color='Call Efficiency',
                         color_continuous_scale='Greens')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Trend analysis
        st.markdown("### 📊 CONVERSION RATE DISTRIBUTION")
        
        fig = px.histogram(df, x='Conversion %', 
                          title="Distribution of Conversion Rates",
                          color_discrete_sequence=[IRONLADY_COLORS['primary']])
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        st.markdown("---")
        st.markdown("### 🔗 ACTIVITY CORRELATION")
        
        corr_data = df[['WA Audit', 'Call Audit', 'SL Calls', 'Total Pitches', 'Total Registrations']].corr()
        
        fig = px.imshow(corr_data, 
                       title="Correlation Matrix",
                       color_continuous_scale='RdBu',
                       aspect='auto')
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("📝 No analytics data available yet.")

# ============================================
# TAB 4: DOCUMENT UPLOAD WITH OCR/NER
# ============================================

def show_document_upload():
    """Enhanced document upload with OCR and NER"""
    
    st.markdown("### 📁 DOCUMENT MANAGEMENT WITH OCR/NER")
    
    st.markdown(f"""
    <div class="info-msg">
        📤 <strong>Upload & Analyze Documents</strong><br/>
        • Upload screenshots, PDFs, images<br/>
        • Automatic text extraction (OCR)<br/>
        • Entity recognition (names, dates, numbers)<br/>
        • Metric extraction (pitches, registrations, leads)<br/>
        • All results included in email reports
    </div>
    """, unsafe_allow_html=True)
    
    # Check availability
    col1, col2, col3 = st.columns(3)
    with col1:
        status = "✅ Available" if OCR_AVAILABLE else "❌ Not installed"
        st.metric("OCR Status", status)
    with col2:
        status = "✅ Available" if NER_AVAILABLE else "❌ Not installed"
        st.metric("NER Status", status)
    with col3:
        status = "✅ Available" if CV2_AVAILABLE else "❌ Not installed"
        st.metric("Image Processing", status)
    
    if not OCR_AVAILABLE:
        st.warning("⚠️ To enable OCR: `pip install pytesseract pillow opencv-python`")
        st.info("💡 Also install Tesseract: https://github.com/tesseract-ocr/tesseract")
    
    if not NER_AVAILABLE:
        st.warning("⚠️ To enable NER: `pip install spacy && python -m spacy download en_core_web_sm`")
    
    st.markdown("---")
    
    # File upload section
    st.markdown("### 📤 UPLOAD DOCUMENTS")
    
    upload_categories = {
        'WA Audit Screenshots': 'wa_audit',
        'SL Status Screenshots': 'sl_status',
        'Call Audit Screenshots': 'call_audit',
        'Performance Reports': 'reports',
        'Other Documents': 'other'
    }
    
    selected_category = st.selectbox("Select Category", list(upload_categories.keys()))
    category_key = upload_categories[selected_category]
    
    uploaded_files = st.file_uploader(
        f"Upload files for {selected_category}",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'xlsx'],
        key=f"uploader_{category_key}"
    )
    
    if uploaded_files:
        user = st.session_state.current_user
        
        if user not in st.session_state.uploaded_documents:
            st.session_state.uploaded_documents[user] = {}
        
        if category_key not in st.session_state.uploaded_documents[user]:
            st.session_state.uploaded_documents[user][category_key] = []
        
        for uploaded_file in uploaded_files:
            file_details = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.type,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'category': selected_category
            }
            
            # Process image files with OCR
            if uploaded_file.type.startswith('image/'):
                st.markdown(f"#### 🖼️ Processing: {uploaded_file.name}")
                
                # Display image
                image = Image.open(uploaded_file)
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(image, caption=uploaded_file.name, use_column_width=True)
                
                with col2:
                    if OCR_AVAILABLE:
                        with st.spinner("🔍 Extracting text with OCR..."):
                            text, error = extract_text_from_image(image)
                            
                            if text:
                                st.success("✅ OCR Complete")
                                
                                # Store OCR result
                                file_details['ocr_text'] = text
                                file_details['has_ocr'] = True
                                
                                # Show extracted text
                                with st.expander("📄 Extracted Text", expanded=True):
                                    st.text_area("OCR Output", text, height=200, key=f"ocr_{uploaded_file.name}")
                                
                                # NER Analysis
                                if NER_AVAILABLE and text.strip():
                                    with st.spinner("🧠 Analyzing entities..."):
                                        entities, error = extract_entities(text)
                                        
                                        if entities:
                                            file_details['entities'] = entities
                                            file_details['has_ner'] = True
                                            
                                            st.markdown("##### 🎯 Extracted Entities")
                                            
                                            # Display entities in columns
                                            ent_col1, ent_col2 = st.columns(2)
                                            
                                            with ent_col1:
                                                if entities.get('PERSON'):
                                                    st.markdown("**👤 People:**")
                                                    for person in entities['PERSON']:
                                                        st.markdown(f"- {person}")
                                                
                                                if entities.get('DATE'):
                                                    st.markdown("**📅 Dates:**")
                                                    for date in entities['DATE']:
                                                        st.markdown(f"- {date}")
                                                
                                                if entities.get('PHONE'):
                                                    st.markdown("**📞 Phone Numbers:**")
                                                    for phone in entities['PHONE']:
                                                        st.markdown(f"- {phone}")
                                            
                                            with ent_col2:
                                                if entities.get('ORG'):
                                                    st.markdown("**🏢 Organizations:**")
                                                    for org in entities['ORG']:
                                                        st.markdown(f"- {org}")
                                                
                                                if entities.get('CARDINAL'):
                                                    st.markdown("**🔢 Numbers:**")
                                                    for num in entities['CARDINAL'][:5]:  # Show first 5
                                                        st.markdown(f"- {num}")
                                                
                                                if entities.get('EMAIL'):
                                                    st.markdown("**📧 Emails:**")
                                                    for email in entities['EMAIL']:
                                                        st.markdown(f"- {email}")
                                        
                                        # Extract metrics
                                        metrics = extract_metrics_from_text(text)
                                        if any(metrics.values()):
                                            file_details['metrics'] = metrics
                                            
                                            st.markdown("##### 📊 Detected Metrics")
                                            met_cols = st.columns(4)
                                            
                                            with met_cols[0]:
                                                if metrics['pitches']:
                                                    st.metric("Pitches", metrics['pitches'][0])
                                            with met_cols[1]:
                                                if metrics['registrations']:
                                                    st.metric("Registrations", metrics['registrations'][0])
                                            with met_cols[2]:
                                                if metrics['leads']:
                                                    st.metric("Leads", metrics['leads'][0])
                                            with met_cols[3]:
                                                if metrics['rms']:
                                                    st.metric("RMs", metrics['rms'][0])
                            else:
                                st.warning(f"⚠️ Could not extract text: {error}")
                    else:
                        st.info("💡 OCR not available. Install pytesseract to extract text.")
            
            else:
                # Non-image files
                st.markdown(f"✅ **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            
            # Store file details
            st.session_state.uploaded_documents[user][category_key].append(file_details)
        
        st.success(f"✅ Processed {len(uploaded_files)} file(s)")
        st.markdown("---")
    
    # Display all uploaded documents
    user = st.session_state.current_user
    if user in st.session_state.uploaded_documents:
        st.markdown("### 📋 UPLOADED DOCUMENTS")
        
        all_docs = []
        for category, docs in st.session_state.uploaded_documents[user].items():
            all_docs.extend(docs)
        
        if all_docs:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", len(all_docs))
            with col2:
                ocr_count = sum(1 for doc in all_docs if doc.get('has_ocr'))
                st.metric("OCR Processed", ocr_count)
            with col3:
                ner_count = sum(1 for doc in all_docs if doc.get('has_ner'))
                st.metric("NER Analyzed", ner_count)
            with col4:
                metrics_count = sum(1 for doc in all_docs if doc.get('metrics'))
                st.metric("Metrics Found", metrics_count)
            
            st.markdown("---")
            
            # Create DataFrame
            df_docs = pd.DataFrame(all_docs)
            
            # Display table
            display_cols = ['name', 'category', 'upload_time', 'size']
            display_df = df_docs[display_cols].copy()
            display_df['size'] = display_df['size'].apply(lambda x: f"{x/1024:.1f} KB")
            display_df.columns = ['File Name', 'Category', 'Upload Time', 'Size']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download button for OCR results
            if ocr_count > 0:
                st.markdown("#### 📥 EXPORT OCR RESULTS")
                
                # Create export data
                export_data = []
                for doc in all_docs:
                    if doc.get('has_ocr'):
                        export_data.append({
                            'File Name': doc['name'],
                            'Category': doc['category'],
                            'Upload Time': doc['upload_time'],
                            'Extracted Text': doc.get('ocr_text', ''),
                            'Entities': json.dumps(doc.get('entities', {})),
                            'Metrics': json.dumps(doc.get('metrics', {}))
                        })
                
                if export_data:
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False)
                    
                    st.download_button(
                        "⬇️ Download OCR Results (CSV)",
                        data=csv,
                        file_name=f"ocr_results_{user}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Clear button
            if st.button("🗑️ Clear All Documents", use_container_width=True):
                st.session_state.uploaded_documents[user] = {}
                st.success("✅ All documents cleared")
                st.rerun()
        
        else:
            st.info("📝 No documents uploaded yet")

# ============================================
# TAB 5: AI INSIGHTS
# ============================================

def show_ai_insights():
    """Show AI-powered insights"""
    
    st.markdown("# 🤖 AI-POWERED INSIGHTS")
    st.markdown("---")
    
    team_data_list = []
    for username, user_info in USERS.items():
        if username in st.session_state.team_data:
            data = st.session_state.team_data[username]
            team_data_list.append({
                'Team Leader': user_info['name'],
                'Pitches': data.get('total_pitches', 0),
                'Registrations': data.get('total_registrations', 0),
                'Conversion %': data.get('conversion_rate', 0),
                'WA Audit': data.get('total_wa_audit', 0),
                'Call Audit': data.get('total_call_audit', 0),
                'SL Calls': data.get('total_sl_calls', 0)
            })
    
    if team_data_list:
        df = pd.DataFrame(team_data_list)
        
        # AI Recommendations
        st.markdown("### 🎯 PERSONALIZED RECOMMENDATIONS")
        
        for _, row in df.iterrows():
            with st.expander(f"📊 {row['Team Leader']}'s Action Plan", expanded=True):
                conversion = row['Conversion %']
                
                # Calculate activity ratios
                total_audits = row['WA Audit'] + row['Call Audit']
                audit_to_pitch_ratio = round((total_audits / row['Pitches']) * 100, 1) if row['Pitches'] > 0 else 0
                
                if conversion >= 15:
                    st.markdown(f"""
                    <div class="success-msg">
                        <h4>✅ Excellent Performance!</h4>
                        <p>Conversion rate: {conversion}% (Target: 15%)</p>
                        <p><strong>Keep it up! Here's how to maintain momentum:</strong></p>
                        <ul>
                            <li>📝 Document your best practices for WA Audit ({int(row['WA Audit'])}) and Call Audit ({int(row['Call Audit'])})</li>
                            <li>🤝 Share techniques with the team - your SL Calls ({int(row['SL Calls'])}) approach is working!</li>
                            <li>✅ Focus on quality leads</li>
                            <li>📞 Maintain consistent follow-up</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif conversion >= 10:
                    st.markdown(f"""
                    <div class="warning-msg">
                        <h4>⚠️ Good Progress, Room for Improvement</h4>
                        <p>Conversion rate: {conversion}% (Target: 15%)</p>
                        <p><strong>Audit Activity Analysis:</strong></p>
                        <ul>
                            <li>WA Audit: {int(row['WA Audit'])} | Call Audit: {int(row['Call Audit'])} | SL Calls: {int(row['SL Calls'])}</li>
                            <li>Audit-to-Pitch Ratio: {audit_to_pitch_ratio}%</li>
                        </ul>
                        <p><strong>Recommendations:</strong></p>
                        <ul>
                            <li>📊 Analyze successful vs unsuccessful pitches</li>
                            <li>💡 Improve pitch quality over quantity</li>
                            <li>📈 Increase WA Audit frequency (target: {int(row['WA Audit'] * 1.2)}+)</li>
                            <li>🎯 Focus on warm leads from SL calls</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="warning-msg">
                        <h4>🎯 Action Required</h4>
                        <p>Conversion rate: {conversion}% (Target: 15%)</p>
                        <p><strong>Current Activity Levels:</strong></p>
                        <ul>
                            <li>WA Audit: {int(row['WA Audit'])} | Call Audit: {int(row['Call Audit'])} | SL Calls: {int(row['SL Calls'])}</li>
                        </ul>
                        <p><strong>Priority Actions:</strong></p>
                        <ul>
                            <li><strong>Immediate:</strong> Review pitch script and techniques</li>
                            <li><strong>This Week:</strong> Increase WA Audit to 15+ and Call Audit to 10+</li>
                            <li><strong>Daily:</strong> Conduct 10+ SL calls with proper follow-up</li>
                            <li><strong>Focus:</strong> Quality audits lead to better pitches</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Team insights
        st.markdown("### 📈 TEAM-WIDE INSIGHTS")
        
        total_pitches = df['Pitches'].sum()
        total_regs = df['Registrations'].sum()
        avg_conversion = round((total_regs / total_pitches * 100), 1) if total_pitches > 0 else 0
        
        total_wa = df['WA Audit'].sum()
        total_ca = df['Call Audit'].sum()
        total_sl = df['SL Calls'].sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-msg">
                <h4>📊 Team Performance</h4>
                <p><strong>Pitches:</strong> {int(total_pitches)}</p>
                <p><strong>Registrations:</strong> {int(total_regs)}</p>
                <p><strong>Team Conversion:</strong> {avg_conversion}%</p>
                <hr style="margin: 10px 0;">
                <p><strong>Activity Totals:</strong></p>
                <p>WA Audits: {int(total_wa)} | Call Audits: {int(total_ca)} | SL Calls: {int(total_sl)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            best = df.loc[df['Conversion %'].idxmax()]
            st.markdown(f"""
            <div class="success-msg">
                <h4>🏆 Best Practices From</h4>
                <p><strong>{best['Team Leader']}</strong></p>
                <p>Conversion Rate: {best['Conversion %']}%</p>
                <p>Activity Profile:</p>
                <ul>
                    <li>WA Audit: {int(best['WA Audit'])}</li>
                    <li>Call Audit: {int(best['Call Audit'])}</li>
                    <li>SL Calls: {int(best['SL Calls'])}</li>
                </ul>
                <p><em>📚 Schedule knowledge sharing session!</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("📝 No data available for AI insights yet.")

# ============================================
# TAB 6: DAILY CHECKLIST
# ============================================

def show_daily_checklist():
    """Show daily checklist"""
    
    st.markdown("# ✅ DAILY CHECKLIST")
    
    # Important warning about saving
    st.warning("⚠️ **IMPORTANT:** Checklist progress resets on page refresh! Click '💾 Save Progress' button below to download your progress, then upload it when you return.")
    
    # Upload saved checklist - PROMINENT POSITION AT TOP
    with st.expander("📤 RESTORE SAVED PROGRESS", expanded=False):
        uploaded_checklist = st.file_uploader("Upload your saved checklist JSON file", type=['json'], key="checklist_upload")
        if uploaded_checklist:
            try:
                saved_data = json.load(uploaded_checklist)
                st.session_state.checklist_state = saved_data
                st.success("✅ Checklist progress restored!")
                st.rerun()
            except:
                st.error("❌ Invalid checklist file")
    
    st.markdown("---")
    
    user = st.session_state.current_user
    
    # Day type selector
    day_type = st.selectbox("Select Day Type", list(DAILY_CHECKLISTS.keys()))
    
    st.markdown(f"### 📋 {day_type} Checklist")
    
    # Initialize checklist state for user
    if user not in st.session_state.checklist_state:
        st.session_state.checklist_state[user] = {}
    
    if day_type not in st.session_state.checklist_state[user]:
        st.session_state.checklist_state[user][day_type] = {}
    
    tasks = DAILY_CHECKLISTS[day_type]['tasks']
    completed_count = 0
    
    # Display tasks
    for idx, task in enumerate(tasks):
        task_key = f"{user}_{day_type}_{idx}"
        
        # Get completion status
        is_completed = st.session_state.checklist_state[user][day_type].get(idx, False)
        
        if is_completed:
            completed_count += 1
        
        # Task row
        col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
        
        with col1:
            checkbox = st.checkbox("", value=is_completed, key=task_key)
            st.session_state.checklist_state[user][day_type][idx] = checkbox
        
        with col2:
            style = "text-decoration: line-through; opacity: 0.6;" if is_completed else ""
            st.markdown(f"<p style='{style}'>{task['name']}</p>", unsafe_allow_html=True)
        
        with col3:
            priority_color = {
                'high': IRONLADY_COLORS['primary'],
                'medium': IRONLADY_COLORS['warning']
            }
            color = priority_color.get(task['priority'], IRONLADY_COLORS['info'])
            st.markdown(f"<span style='background: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8rem;'>{task['priority'].upper()}</span>", unsafe_allow_html=True)
        
        with col4:
            type_icons = {
                'upload': '📤',
                'manual': '✍️',
                'ongoing': '🔄'
            }
            icon = type_icons.get(task['type'], '📝')
            st.markdown(f"<span style='font-size: 0.9rem;'>{icon} {task['type']}</span>", unsafe_allow_html=True)
    
    # Progress
    progress = (completed_count / len(tasks)) * 100
    
    st.markdown("---")
    st.markdown("### 📊 PROGRESS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Completed", f"{completed_count}/{len(tasks)}")
    
    with col2:
        st.metric("Progress", f"{progress:.0f}%")
    
    with col3:
        if progress == 100:
            st.success("🎉 All Done!")
        elif progress >= 50:
            st.info("💪 Keep Going!")
        else:
            st.warning("⚡ Let's Start!")
    
    st.progress(progress / 100)
    
    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Mark All Complete", use_container_width=True):
            for idx in range(len(tasks)):
                st.session_state.checklist_state[user][day_type][idx] = True
            st.success("✅ All tasks marked complete!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Checklist", use_container_width=True):
            st.session_state.checklist_state[user][day_type] = {}
            st.success("🔄 Checklist reset!")
            st.rerun()
    
    with col3:
        # Download checklist state
        checklist_json = json.dumps(st.session_state.checklist_state, indent=2)
        st.download_button(
            label="💾 Save Progress",
            data=checklist_json,
            file_name=f"checklist_{user}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# ============================================
# MAIN APP
# ============================================

def main():
    """Main application"""
    
    if not st.session_state.logged_in:
        show_login()
    else:
        show_sidebar()
        
        # Main content tabs
        tabs = st.tabs([
            "📊 My Dashboard",
            "🏆 Team Performance",
            "📈 Analytics",
            "📁 Documents (OCR/NER)",
            "🤖 AI Insights",
            "✅ Daily Checklist"
        ])
        
        with tabs[0]:
            show_my_dashboard()
        
        with tabs[1]:
            show_team_performance()
        
        with tabs[2]:
            show_analytics()
        
        with tabs[3]:
            show_document_upload()
        
        with tabs[4]:
            show_ai_insights()
        
        with tabs[5]:
            show_daily_checklist()

if __name__ == "__main__":
    main()
