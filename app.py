"""
IRON LADY SALES TRACKER - FINAL PROFESSIONAL VERSION
Complete Dashboard with Manual RM Data Entry & Official Branding
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from PIL import Image
import io
import json

# Load environment variables
load_dotenv()

# Try to import OCR libraries
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
    'primary': '#E63946',      # Iron Lady Red (main brand color)
    'secondary': '#1A1A1A',    # Black (text and icons)
    'accent': '#F5E6D3',       # Beige/Cream (background)
    'success': '#2A9D8F',      # Teal Green
    'warning': '#F77F00',      # Orange
    'danger': '#D62828',       # Dark Red
    'light': '#FAF3E0',        # Light Cream
    'dark': '#1A1A1A',         # Black
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

# Official Iron Lady Custom CSS
st.markdown(f"""
<style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Main Header */
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
    
    /* Iron Lady Logo Container */
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
    
    /* Cards */
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
    
    /* Data Entry Card */
    .data-entry-card {{
        background: white;
        padding: 25px;
        border-radius: 0px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 6px solid {IRONLADY_COLORS['primary']};
        margin: 20px 0;
    }}
    
    /* Login Cards */
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
    
    /* Success/Error Messages */
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
    
    /* Input Fields */
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
    
    /* Checklist Items */
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
    
    /* Badges */
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
    
    /* Status Badges */
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
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {IRONLADY_COLORS['dark']} 0%, {IRONLADY_COLORS['secondary']} 100%);
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Progress Bar */
    .stProgress > div > div > div {{
        background: {IRONLADY_COLORS['primary']};
    }}
    
    /* Buttons */
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
    
    /* Tables */
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
    
    /* Section Headers */
    h2, h3 {{
        color: {IRONLADY_COLORS['dark']};
        font-weight: 900;
        border-bottom: 4px solid {IRONLADY_COLORS['primary']};
        padding-bottom: 10px;
        margin-top: 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Divider */
    hr {{
        border: none;
        height: 3px;
        background: {IRONLADY_COLORS['primary']};
        margin: 30px 0;
    }}
    
    /* Tab Styling */
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
    
    /* File Uploader */
    .stFileUploader {{
        border: 2px dashed {IRONLADY_COLORS['primary']};
        border-radius: 0px;
        padding: 20px;
        background: {IRONLADY_COLORS['light']};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {IRONLADY_COLORS['light']};
        border-radius: 0px;
        font-weight: 700;
        color: {IRONLADY_COLORS['dark']};
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 20px;
        color: {IRONLADY_COLORS['dark']};
        font-size: 0.85rem;
        margin-top: 50px;
        border-top: 3px solid {IRONLADY_COLORS['primary']};
        background: {IRONLADY_COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'team_leads' not in st.session_state:
    st.session_state.team_leads = [
        'Ghazala',
        'Megha',
        'Afreen',
        'Soumya'
    ]

if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize RM data for each team lead with proper structure
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

# ============================================
# LOGIN SECTION
# ============================================

def show_login_page():
    """Display official Iron Lady branded login page"""
    
    # Logo/Branding Section
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
        
        # Display existing team leads in a grid
        cols = st.columns(2)
        for idx, lead in enumerate(st.session_state.team_leads):
            with cols[idx % 2]:
                if st.button(f"👤 {lead}", key=f"login_{idx}", use_container_width=True):
                    st.session_state.user = lead
                    st.session_state.checklist = {}
                    # Initialize RM data for this user if not exists
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
        
        # Add new team lead option
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
                            # Initialize RM data for new user
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
                            # Initialize RM data for new user
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
    
    # Calculate conversion rate
    if metrics['total_actual_pitch'] > 0:
        metrics['conversion_rate'] = round(
            (metrics['total_actual_reg'] / metrics['total_actual_pitch']) * 100, 1
        )
    else:
        metrics['conversion_rate'] = 0
    
    # Calculate achievements
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
# DATA ENTRY INTERFACE
# ============================================

def show_data_entry_interface():
    """Display professional data entry interface for RM metrics"""
    st.markdown("### 📝 MANUAL DATA ENTRY")
    
    st.markdown('<div class="info-msg">💡 <strong>Instructions:</strong> Enter your team\'s performance data below. You can add multiple entries for different RMs or teams.</div>', unsafe_allow_html=True)
    
    current_data = get_current_user_data()
    
    # Add new entry form
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
                    # Check if entry already exists
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
                        
                        # Remove empty rows before adding
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
    
    # Display existing entries
    st.markdown("---")
    st.markdown("### 📊 CURRENT ENTRIES")
    
    display_data = current_data[current_data['RM_Name'] != ''].copy()
    
    if len(display_data) > 0:
        # Calculate conversion rate for display
        display_data['Conversion %'] = display_data.apply(
            lambda row: round((row['Actual_Registration'] / row['Actual_Pitch'] * 100), 1) 
            if row['Actual_Pitch'] > 0 else 0,
            axis=1
        )
        
        # Display as editable dataframe
        st.dataframe(
            display_data[['RM_Name', 'Total_RMs', 'Lead_Count', 'Target_Pitch', 
                         'Actual_Pitch', 'Target_Registration', 'Actual_Registration', 'Conversion %']],
            use_container_width=True,
            hide_index=True
        )
        
        # Edit and Delete options
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
        
        # Quick summary
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
# MAIN APP
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
        
        st.markdown("### 📊 QUICK STATS")
        current_data = get_current_user_data()
        metrics = calculate_metrics(current_data)
        
        st.metric("Total RMs", metrics['total_rms'])
        st.metric("Total Leads", metrics['total_leads'], delta=None)
        st.metric("Pitch Achievement", f"{metrics['pitch_achievement']}%")
        st.metric("Registration Achievement", f"{metrics['reg_achievement']}%")
        st.metric("Conversion Rate", f"{metrics['conversion_rate']}%")
        
        st.markdown("---")
        
        # System info
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 0px; margin-top: 20px; border-left: 3px solid {IRONLADY_COLORS['primary']};">
            <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">
                <strong>System Status:</strong><br/>
                ✅ Connected<br/>
                🕐 Last Updated: {datetime.now().strftime('%I:%M %p')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tab structure
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 DATA ENTRY",
        "📊 PERFORMANCE DASHBOARD",
        "📁 DOCUMENT MANAGEMENT",
        "✅ DAILY CHECKLIST"
    ])
    
    # ============================================
    # TAB 1: DATA ENTRY
    # ============================================
    
    with tab1:
        show_data_entry_interface()
    
    # ============================================
    # TAB 2: DASHBOARD
    # ============================================
    
    with tab2:
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
            # RM-wise conversion rate
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
            # Target vs Actual
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
    # TAB 3: FILE UPLOAD
    # ============================================
    
    with tab3:
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
                    for uploaded_file in uploaded_files:
                        file_size = uploaded_file.size / 1024  # Convert to KB
                        st.markdown(f'<div class="success-msg">✅ <strong>{uploaded_file.name}</strong> ({file_size:.1f} KB) ready to upload</div>', unsafe_allow_html=True)
                        st.session_state.files_uploaded[file_info['key']] = uploaded_file.name
    
    # ============================================
    # TAB 4: CHECKLIST
    # ============================================
    
    with tab4:
        st.markdown("### ✅ DAILY ACTIVITY CHECKLIST")
        
        checklist_items = {
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
        
        selected_checklist = checklist_items.get(st.session_state.selected_day, [])
        
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
            st.markdown(f"#### 🔴 HIGH PRIORITY TASKS")
            render_checklist_items(high_priority, 'high')
        
        # Medium Priority Tasks
        if medium_priority:
            st.markdown("---")
            st.markdown(f"#### 🟡 MEDIUM PRIORITY TASKS")
            render_checklist_items(medium_priority, 'medium')
        
        # Low Priority Tasks
        if low_priority:
            st.markdown("---")
            st.markdown(f"#### 🟢 STANDARD TASKS")
            render_checklist_items(low_priority, 'low')
        
        st.markdown("---")
        
        # Calculate progress
        task_names = [item['task'] for item in selected_checklist]
        checked_count = sum(1 for task in task_names if st.session_state.checklist.get(task, False))
        progress = checked_count / len(task_names) * 100 if task_names else 0
        
        # Progress bar with custom styling
        st.markdown(f"""
        <div style="background: {IRONLADY_COLORS['light']}; padding: 20px; border-radius: 0px; margin: 20px 0; border-left: 5px solid {IRONLADY_COLORS['primary']};">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0 0 10px 0; font-weight: 900; text-transform: uppercase;">OVERALL PROGRESS</h4>
        """, unsafe_allow_html=True)
        
        st.progress(progress / 100, text=f"{progress:.0f}% Complete")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="✅ Completed", value=f"{checked_count}/{len(task_names)}")
        
        with col2:
            st.metric(label="⏳ Remaining", value=f"{len(task_names) - checked_count}/{len(task_names)}")
        
        with col3:
            if checked_count == len(task_names) and len(task_names) > 0:
                st.markdown('<div class="success-msg">🎉 <strong>All tasks completed!</strong> Excellent work!</div>', unsafe_allow_html=True)
            else:
                remaining_pct = ((len(task_names) - checked_count) / len(task_names) * 100) if task_names else 0
                st.metric(label="📊 Completion Rate", value=f"{100-remaining_pct:.0f}%")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p style="font-weight: 900; text-transform: uppercase; letter-spacing: 2px; font-size: 1.1rem; color: {IRONLADY_COLORS['primary']};">IRON LADY SALES TRACKER</p>
        <p style="font-weight: 600;">Official Branded Edition with Manual Data Entry | v3.5</p>
        <p style="font-size: 0.75rem; opacity: 0.7; margin-top: 10px;">© 2024 Iron Lady. All rights reserved. | Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

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

if __name__ == "__main__":
    main()