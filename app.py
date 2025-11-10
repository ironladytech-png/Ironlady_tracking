"""
IRON LADY - Complete Dashboard (Fixed Version)
Table-Based Data Entry + Daily Checklist + Document Upload
Single file, SQLite database, Professional interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
import os
import io

# ============================================
# DATABASE SETUP WITH ERROR HANDLING
# ============================================

def init_database():
    """Initialize SQLite database with error handling"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                team_size INTEGER NOT NULL
            )
        ''')
        
        # RM details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rm_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                rm_name TEXT NOT NULL,
                UNIQUE(username, rm_name)
            )
        ''')
        
        # Daily RM metrics table (for each RM, each date)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rm_daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                rm_name TEXT NOT NULL,
                date TEXT NOT NULL,
                wa_audit_target INTEGER DEFAULT 0,
                wa_audit_achieved INTEGER DEFAULT 0,
                call_audit_target INTEGER DEFAULT 0,
                call_audit_achieved INTEGER DEFAULT 0,
                mocks_target INTEGER DEFAULT 0,
                mocks_achieved INTEGER DEFAULT 0,
                sl_calls_target INTEGER DEFAULT 0,
                sl_calls_achieved INTEGER DEFAULT 0,
                followups_target INTEGER DEFAULT 0,
                followups_achieved INTEGER DEFAULT 0,
                pitches_target INTEGER DEFAULT 0,
                pitches_achieved INTEGER DEFAULT 0,
                current_mc_target INTEGER DEFAULT 0,
                current_mc_achieved INTEGER DEFAULT 0,
                sign_off_task TEXT DEFAULT '',
                potential_list TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                UNIQUE(username, rm_name, date)
            )
        ''')
        
        # Checklists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                day_type TEXT NOT NULL,
                task_index INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                UNIQUE(username, date, day_type, task_index)
            )
        ''')
        
        # Uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                filename TEXT NOT NULL,
                filesize INTEGER NOT NULL,
                filetype TEXT NOT NULL,
                upload_time TEXT NOT NULL
            )
        ''')
        
        # Insert default users
        default_users = [
            ('ghazala', 'ironlady2024', 'Ghazala - Rising Stars', 'Senior Team Leader', 7),
            ('megha', 'ironlady2024', 'Megha - Winners', 'Senior Team Leader', 4),
            ('afreen', 'ironlady2024', 'Afreen - High Flyers', 'Trainee Team Leader', 4),
            ('soumya', 'ironlady2024', 'Soumya - Goal Getters', 'Trainee Team Leader', 3)
        ]
        
        for user in default_users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, name, role, team_size)
                VALUES (?, ?, ?, ?, ?)
            ''', user)
        
        # Insert default RMs
        default_rms = [
            ('ghazala', 'Kajal'),
            ('ghazala', 'Shivani'),
            ('ghazala', 'Priyanka'),
            ('ghazala', 'Farha'),
            ('ghazala', 'Shri'),
            ('ghazala', 'Pooja'),
            ('ghazala', 'Anum'),
            ('megha', 'RM1'),
            ('megha', 'RM2'),
            ('megha', 'RM3'),
            ('megha', 'RM4'),
            ('afreen', 'Beni'),
            ('afreen', 'Smruti'),
            ('afreen', 'Kaarti'),
            ('afreen', 'Deepesh'),
            ('soumya', 'Akansha'),
            ('soumya', 'Abhinaya'),
            ('soumya', 'Sharan'),
        ]
        
        for rm in default_rms:
            cursor.execute('''
                INSERT OR IGNORE INTO rm_details (username, rm_name)
                VALUES (?, ?)
            ''', rm)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False

# Initialize database
init_database()

# ============================================
# CONFIGURATION
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
    'warning': '#F4A261',
    'info': '#457B9D'
}

DAILY_CHECKLISTS = {
    'Day 1-1': [
        {'task': 'Mocks - Who are the people - Buddy structure', 'priority': 'high'},
        {'task': 'Sign off Activities - each RM type', 'priority': 'high'},
        {'task': 'WA Audit - Minimum 10', 'priority': 'high'},
        {'task': 'Follow up Calls - 2 Registrations', 'priority': 'high'},
        {'task': 'SL Calls - 5 (Share status list)', 'priority': 'high'},
        {'task': 'Lead Analysis AI summary', 'priority': 'medium'},
        {'task': 'Call Audit - Minimum 5 calls', 'priority': 'high'},
        {'task': 'Tracking: CRM Update, Call/Attendance/WA', 'priority': 'medium'},
        {'task': 'Targets Sharing - percentage and potential list', 'priority': 'medium'},
        {'task': 'CRM Updation', 'priority': 'medium'},
        {'task': 'Sharing hot prospects list', 'priority': 'medium'},
    ],
    'Day 1': [
        {'task': 'WA Audit - 10', 'priority': 'high'},
        {'task': 'SL Calls - 8 (Share status list)', 'priority': 'high'},
        {'task': 'Sign off Activities', 'priority': 'high'},
        {'task': 'Mocks - Buddy structure', 'priority': 'high'},
        {'task': '30s pitch Prep', 'priority': 'medium'},
        {'task': 'Tracking: CRM Update', 'priority': 'medium'},
        {'task': 'Call Audit - Minimum 5 calls', 'priority': 'high'},
        {'task': 'Targets Sharing - % and potential list', 'priority': 'medium'},
        {'task': '10% Conversion - action points', 'priority': 'high'},
        {'task': 'CRM Updation - including attendance', 'priority': 'medium'},
        {'task': 'Sharing hot prospects list and Tracking', 'priority': 'medium'},
    ],
    'Day 2': [
        {'task': 'SL Calls - 10-12 (Share status list)', 'priority': 'high'},
        {'task': 'WA Audit - As needed', 'priority': 'medium'},
        {'task': 'Tracking: CRM Update', 'priority': 'medium'},
        {'task': 'Sign off Activities', 'priority': 'high'},
        {'task': 'Targets Sharing - 10% before, 15% after', 'priority': 'high'},
        {'task': 'CRM Updation - including attendance', 'priority': 'medium'},
        {'task': 'Sharing hot prospects list and Tracking', 'priority': 'medium'},
    ]
}

UPLOAD_CATEGORIES = [
    {'name': 'WA Audit', 'icon': '💬', 'desc': 'WhatsApp audit reports, screenshots, and conversation exports'},
    {'name': 'Call Recording', 'icon': '📞', 'desc': 'Call recording audits, reports, and app screenshots'},
    {'name': 'Lead Analysis', 'icon': '📊', 'desc': 'Lead analysis reports and AI summaries'},
    {'name': 'Mock Recording', 'icon': '🎯', 'desc': 'Mock call recordings and feedback documents'},
    {'name': 'Daily Report', 'icon': '📋', 'desc': 'Daily performance reports and summaries'},
    {'name': 'SL Call Report', 'icon': '📝', 'desc': 'Short list status documents and tracking screenshots'},
    {'name': 'Hot Prospects List', 'icon': '🔥', 'desc': 'High-priority prospect lists and screenshots'},
    {'name': 'Other', 'icon': '📄', 'desc': 'Additional supporting documents and screenshots'}
]

# ============================================
# STYLING
# ============================================

st.set_page_config(
    page_title="Iron Lady Dashboard",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
<style>
    .main {{
        background-color: {IRONLADY_COLORS['accent']};
    }}
    .stButton>button {{
        background-color: {IRONLADY_COLORS['primary']};
        color: white;
        font-weight: 700;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
    }}
    .stButton>button:hover {{
        background-color: {IRONLADY_COLORS['secondary']};
    }}
    .success-msg {{
        background-color: {IRONLADY_COLORS['success']};
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    .info-msg {{
        background-color: {IRONLADY_COLORS['info']};
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    .warning-msg {{
        background-color: {IRONLADY_COLORS['warning']};
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    .dataframe {{
        font-size: 12px !important;
    }}
    .stDataFrame {{
        width: 100% !important;
    }}
    .task-item {{
        padding: 12px;
        margin: 8px 0;
        background: white;
        border-radius: 8px;
        border-left: 4px solid {IRONLADY_COLORS['primary']};
    }}
    .upload-card {{
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border: 2px solid {IRONLADY_COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# ============================================
# DATABASE FUNCTIONS WITH ERROR HANDLING
# ============================================

def get_user(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'username': user[0],
                'name': user[2],
                'role': user[3],
                'team_size': user[4]
            }
        return None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

def get_user_rms(username):
    """Get list of RMs for a user"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT rm_name FROM rm_details WHERE username = ? ORDER BY rm_name', (username,))
        rms = [row[0] for row in cursor.fetchall()]
        conn.close()
        return rms
    except Exception as e:
        st.error(f"Error loading RMs: {str(e)}")
        return []

def add_rm(username, rm_name):
    """Add new RM"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO rm_details (username, rm_name) VALUES (?, ?)', (username, rm_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding RM: {str(e)}")
        return False

def delete_rm(username, rm_name):
    """Delete RM"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rm_details WHERE username = ? AND rm_name = ?', (username, rm_name))
        cursor.execute('DELETE FROM rm_daily_metrics WHERE username = ? AND rm_name = ?', (username, rm_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting RM: {str(e)}")
        return False

def save_rm_metrics(username, date, metrics_df):
    """Save metrics for all RMs"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for _, row in metrics_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO rm_daily_metrics 
                (username, rm_name, date, wa_audit_target, wa_audit_achieved, call_audit_target, call_audit_achieved,
                 mocks_target, mocks_achieved, sl_calls_target, sl_calls_achieved, followups_target, followups_achieved,
                 pitches_target, pitches_achieved, current_mc_target, current_mc_achieved, sign_off_task, potential_list, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, row['RM Name'], date,
                row.get('WA Audit Target', 0), row.get('WA Audit Achieved', 0),
                row.get('Call Audit Target', 0), row.get('Call Audit Achieved', 0),
                row.get('Mocks Target', 0), row.get('Mocks Achieved', 0),
                row.get('SL Calls Target', 0), row.get('SL Calls Achieved', 0),
                row.get('Follow ups Target', 0), row.get('Follow ups Achieved', 0),
                row.get('Pitches Target', 0), row.get('Pitches Achieved', 0),
                row.get('Current MC Target', 0), row.get('Current MC Achieved', 0),
                row.get('Sign off Task', ''), row.get('Potential List', ''),
                timestamp
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving metrics: {str(e)}")
        return False

def load_rm_metrics(username, date):
    """Load metrics for all RMs for a date"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        query = '''
            SELECT rm_name, wa_audit_target, wa_audit_achieved, call_audit_target, call_audit_achieved,
                   mocks_target, mocks_achieved, sl_calls_target, sl_calls_achieved,
                   followups_target, followups_achieved, pitches_target, pitches_achieved,
                   current_mc_target, current_mc_achieved, sign_off_task, potential_list
            FROM rm_daily_metrics
            WHERE username = ? AND date = ?
            ORDER BY rm_name
        '''
        df = pd.read_sql_query(query, conn, params=(username, date))
        conn.close()
        
        if len(df) > 0:
            df.columns = ['RM Name', 'WA Audit Target', 'WA Audit Achieved', 'Call Audit Target', 'Call Audit Achieved',
                         'Mocks Target', 'Mocks Achieved', 'SL Calls Target', 'SL Calls Achieved',
                         'Follow ups Target', 'Follow ups Achieved', 'Pitches Target', 'Pitches Achieved',
                         'Current MC Target', 'Current MC Achieved', 'Sign off Task', 'Potential List']
            return df
        return None
    except Exception as e:
        st.error(f"Error loading metrics: {str(e)}")
        return None

def save_checklist(username, date, day_type, tasks):
    """Save checklist tasks"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for idx, task in enumerate(tasks):
            cursor.execute('''
                INSERT OR REPLACE INTO checklists 
                (username, date, day_type, task_index, task_name, completed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, date, day_type, idx, task['task'], 1 if task.get('completed', False) else 0, timestamp))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving checklist: {str(e)}")
        return False

def load_checklist(username, date, day_type):
    """Load checklist tasks"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_index, task_name, completed 
            FROM checklists 
            WHERE username = ? AND date = ? AND day_type = ?
            ORDER BY task_index
        ''', (username, date, day_type))
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return {row[1]: bool(row[2]) for row in results}
        return None
    except Exception as e:
        st.error(f"Error loading checklist: {str(e)}")
        return None

def save_upload(username, date, category, filename, filesize, filetype):
    """Save upload record"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO uploads (username, date, category, filename, filesize, filetype, upload_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, date, category, filename, filesize, filetype, upload_time))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving upload: {str(e)}")
        return False

def get_uploads(username, date):
    """Get uploads for a date"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, filename, filesize, filetype, upload_time
            FROM uploads
            WHERE username = ? AND date = ?
            ORDER BY upload_time DESC
        ''', (username, date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        st.error(f"Error loading uploads: {str(e)}")
        return []

def get_team_summary():
    """Get team summary"""
    try:
        conn = sqlite3.connect('ironlady.db', timeout=10)
        query = '''
            SELECT 
                u.name as Team_Leader,
                u.team_size as Total_RMs,
                COALESCE(SUM(m.wa_audit_achieved), 0) as Total_WA_Audit,
                COALESCE(SUM(m.call_audit_achieved), 0) as Total_Call_Audit,
                COALESCE(SUM(m.mocks_achieved), 0) as Total_Mocks,
                COALESCE(SUM(m.sl_calls_achieved), 0) as Total_SL_Calls,
                COALESCE(SUM(m.pitches_achieved), 0) as Total_Pitches,
                COALESCE(SUM(m.followups_achieved), 0) as Total_Registrations,
                COALESCE(SUM(m.current_mc_achieved), 0) as Total_Current_MC
            FROM users u
            LEFT JOIN rm_daily_metrics m ON u.username = m.username
            GROUP BY u.username, u.name, u.team_size
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) > 0:
            df['Conversion_Rate'] = df.apply(
                lambda row: round((row['Total_Registrations'] / row['Total_Pitches'] * 100), 1) 
                if row['Total_Pitches'] > 0 else 0,
                axis=1
            )
        return df
    except Exception as e:
        st.error(f"Error loading team summary: {str(e)}")
        return pd.DataFrame()

# ============================================
# LOGIN PAGE
# ============================================

def show_login():
    """Show login page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="color: {IRONLADY_COLORS['primary']}; font-size: 3rem; font-weight: 900; letter-spacing: 3px;">
                IRON LADY
            </h1>
            <p style="color: {IRONLADY_COLORS['secondary']}; font-size: 1.2rem;">
                Team Performance Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🔑 LOGIN", use_container_width=True)
            
            if submit:
                user = get_user(username.lower(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user['username']
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("💡 **Default Credentials:**\n\nUsername: `ghazala` / `megha` / `afreen` / `soumya`\n\nPassword: `ironlady2024`")

# ============================================
# SIDEBAR
# ============================================

def show_sidebar():
    """Show sidebar"""
    
    user_info = st.session_state.user_info
    
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {IRONLADY_COLORS['primary']}; margin: 0;">IRON LADY</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown(f"### 👤 {user_info['name']}")
    st.sidebar.markdown(f"**{user_info['role']}**")
    st.sidebar.markdown(f"Team Size: **{user_info['team_size']} RMs**")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_info = None
        st.rerun()

# ============================================
# TAB 1: TABLE DATA ENTRY
# ============================================

def show_table_data_entry():
    """Show spreadsheet-style data entry"""
    
    st.markdown("# 📊 Daily Data Entry")
    st.markdown("---")
    
    username = st.session_state.current_user
    user_info = st.session_state.user_info
    
    # Date selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        today = datetime.now().date()
        selected_date = st.date_input("📅 Date", value=today)
        selected_date_str = selected_date.strftime('%Y-%m-%d')
    
    with col2:
        if st.button("📥 Load Data", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🔄 Clear Table", use_container_width=True):
            if 'edited_df' in st.session_state:
                del st.session_state.edited_df
            st.rerun()
    
    st.markdown("---")
    
    # Get RMs
    rms = get_user_rms(username)
    
    if not rms:
        st.warning("⚠️ No RMs configured. Please add RMs in the 'Manage RMs' tab.")
        return
    
    # Load existing data or create template
    existing_df = load_rm_metrics(username, selected_date_str)
    
    if existing_df is not None and len(existing_df) > 0:
        df = existing_df
    else:
        df = pd.DataFrame({
            'RM Name': rms,
            'WA Audit Target': [0] * len(rms),
            'WA Audit Achieved': [0] * len(rms),
            'Call Audit Target': [0] * len(rms),
            'Call Audit Achieved': [0] * len(rms),
            'Mocks Target': [0] * len(rms),
            'Mocks Achieved': [0] * len(rms),
            'SL Calls Target': [0] * len(rms),
            'SL Calls Achieved': [0] * len(rms),
            'Follow ups Target': [0] * len(rms),
            'Follow ups Achieved': [0] * len(rms),
            'Pitches Target': [0] * len(rms),
            'Pitches Achieved': [0] * len(rms),
            'Current MC Target': [0] * len(rms),
            'Current MC Achieved': [0] * len(rms),
            'Sign off Task': [''] * len(rms),
            'Potential List': [''] * len(rms)
        })
    
    # Show team name
    st.markdown(f"### {user_info['name']} - {selected_date.strftime('%B %d, %Y')}")
    
    # Editable data editor
    st.markdown("**📝 Enter data in the table below (spreadsheet-style):**")
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
        column_config={
            "RM Name": st.column_config.TextColumn("RM Name", disabled=True, width="medium"),
            "WA Audit Target": st.column_config.NumberColumn("WA Audit Target", min_value=0, max_value=100, width="small"),
            "WA Audit Achieved": st.column_config.NumberColumn("WA Audit Achieved", min_value=0, max_value=100, width="small"),
            "Call Audit Target": st.column_config.NumberColumn("Call Audit Target", min_value=0, max_value=100, width="small"),
            "Call Audit Achieved": st.column_config.NumberColumn("Call Audit Achieved", min_value=0, max_value=100, width="small"),
            "Mocks Target": st.column_config.NumberColumn("Mocks Target", min_value=0, max_value=50, width="small"),
            "Mocks Achieved": st.column_config.NumberColumn("Mocks Achieved", min_value=0, max_value=50, width="small"),
            "SL Calls Target": st.column_config.NumberColumn("SL Calls Target", min_value=0, max_value=100, width="small"),
            "SL Calls Achieved": st.column_config.NumberColumn("SL Calls Achieved", min_value=0, max_value=100, width="small"),
            "Follow ups Target": st.column_config.NumberColumn("Follow ups Target", min_value=0, max_value=100, width="small"),
            "Follow ups Achieved": st.column_config.NumberColumn("Follow ups Achieved", min_value=0, max_value=100, width="small"),
            "Pitches Target": st.column_config.NumberColumn("Pitches Target", min_value=0, max_value=1000, width="small"),
            "Pitches Achieved": st.column_config.NumberColumn("Pitches Achieved", min_value=0, max_value=1000, width="small"),
            "Current MC Target": st.column_config.NumberColumn("Current MC Target", min_value=0, max_value=100, width="small"),
            "Current MC Achieved": st.column_config.NumberColumn("Current MC Achieved", min_value=0, max_value=100, width="small"),
            "Sign off Task": st.column_config.TextColumn("Sign off Task", width="medium"),
            "Potential List": st.column_config.TextColumn("Potential List", width="medium")
        },
        key="data_editor"
    )
    
    # Calculate totals
    st.markdown("---")
    st.markdown("### 📊 Team Totals")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_wa = int(edited_df['WA Audit Achieved'].sum())
        st.metric("💬 WA Audit", total_wa)
    
    with col2:
        total_call = int(edited_df['Call Audit Achieved'].sum())
        st.metric("📞 Call Audit", total_call)
    
    with col3:
        total_mocks = int(edited_df['Mocks Achieved'].sum())
        st.metric("🎯 Mocks", total_mocks)
    
    with col4:
        total_sl = int(edited_df['SL Calls Achieved'].sum())
        st.metric("📋 SL Calls", total_sl)
    
    with col5:
        total_pitches = int(edited_df['Pitches Achieved'].sum())
        st.metric("📢 Pitches", total_pitches)
    
    with col6:
        total_regs = int(edited_df['Follow ups Achieved'].sum())
        st.metric("📝 Registrations", total_regs)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conversion = round((total_regs / total_pitches * 100), 1) if total_pitches > 0 else 0
        st.metric("💯 Conversion Rate", f"{conversion}%")
    
    with col2:
        total_mc = int(edited_df['Current MC Achieved'].sum())
        st.metric("🎓 MC Registrations", total_mc)
    
    with col3:
        if conversion >= 15:
            st.success("✅ On Target!")
        elif conversion >= 10:
            st.warning(f"⚠️ {15 - conversion:.1f}% below target")
        else:
            st.error(f"❌ {15 - conversion:.1f}% below target")
    
    # Save button
    st.markdown("---")
    
    if st.button("💾 SAVE ALL DATA", use_container_width=True, type="primary"):
        if save_rm_metrics(username, selected_date_str, edited_df):
            st.success(f"✅ Data saved for {len(rms)} RMs on {selected_date_str}!")
            st.balloons()
        else:
            st.error("❌ Error saving data")

# ============================================
# TAB 2: DAILY CHECKLIST
# ============================================

def show_daily_checklist():
    """Show daily checklist"""
    
    st.markdown("# ✅ Daily Checklist")
    st.markdown("---")
    
    username = st.session_state.current_user
    user_info = st.session_state.user_info
    
    # Date and day type selector
    col1, col2 = st.columns([2, 2])
    
    with col1:
        today = datetime.now().date()
        selected_date = st.date_input("📅 Date", value=today, key="checklist_date")
        selected_date_str = selected_date.strftime('%Y-%m-%d')
    
    with col2:
        day_type = st.selectbox("📋 Day Type", options=['Day 1-1', 'Day 1', 'Day 2'], key="day_type")
    
    st.markdown("---")
    
    # Get tasks for selected day type
    tasks = DAILY_CHECKLISTS[day_type]
    
    # Load existing checklist or create new
    saved_checklist = load_checklist(username, selected_date_str, day_type)
    
    if saved_checklist is None:
        # Initialize checklist state
        checklist_state = {task['task']: False for task in tasks}
    else:
        checklist_state = saved_checklist
    
    # Display checklist
    st.markdown(f"### {user_info['name']} - {day_type} - {selected_date.strftime('%B %d, %Y')}")
    
    # Calculate progress
    completed_tasks = [task['task'] for task in tasks if checklist_state.get(task['task'], False)]
    total_tasks = len(tasks)
    completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
    
    st.progress(completion_rate / 100, text=f"Progress: {len(completed_tasks)}/{total_tasks} tasks ({completion_rate:.0f}%)")
    
    st.markdown("---")
    
    # Task list with checkboxes
    updated_tasks = []
    
    for idx, task_item in enumerate(tasks):
        task = task_item['task']
        priority = task_item['priority']
        
        col1, col2 = st.columns([0.08, 0.92])
        
        with col1:
            checked = st.checkbox(
                "", 
                value=checklist_state.get(task, False), 
                key=f"check_{idx}_{task[:20]}", 
                label_visibility="collapsed"
            )
        
        with col2:
            priority_badge = "🔴 HIGH" if priority == "high" else "🟡 MEDIUM"
            status_icon = "✅" if checked else "⏳"
            
            st.markdown(f"""
            <div class="task-item">
                {status_icon} <strong>{task}</strong><br/>
                <small>{priority_badge}</small>
            </div>
            """, unsafe_allow_html=True)
        
        updated_tasks.append({
            'task': task,
            'priority': priority,
            'completed': checked
        })
    
    # Save button
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 SAVE CHECKLIST", use_container_width=True, type="primary"):
            if save_checklist(username, selected_date_str, day_type, updated_tasks):
                st.success(f"✅ Checklist saved! Completed: {len(completed_tasks)}/{total_tasks}")
                st.balloons()
    
    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            st.rerun()

# ============================================
# TAB 3: DOCUMENT UPLOAD
# ============================================

def show_document_upload():
    """Show document upload"""
    
    st.markdown("# 📁 Document Upload")
    st.markdown("---")
    
    username = st.session_state.current_user
    user_info = st.session_state.user_info
    
    # Date selector
    today = datetime.now().date()
    selected_date = st.date_input("📅 Date", value=today, key="upload_date")
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    
    st.markdown("---")
    
    st.markdown(f"""
    <div class="info-msg">
        📤 <strong>Upload Instructions:</strong> Upload your daily reports, documents, and screenshots. 
        Accepted formats: PDF, DOCX, XLSX, PNG, JPG, JPEG. All files are securely tracked.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload categories
    for category_info in UPLOAD_CATEGORIES:
        with st.expander(f"{category_info['icon']} {category_info['name']}", expanded=False):
            st.markdown(f"<p style='color: #666; font-size: 0.9rem;'>{category_info['desc']}</p>", unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                f"Upload {category_info['name'].lower()}",
                key=f"uploader_{category_info['name']}",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif']
            )
            
            if uploaded_files:
                st.markdown("#### 📤 Uploaded Files:")
                for uploaded_file in uploaded_files:
                    file_size = uploaded_file.size / 1024  # KB
                    
                    # Save to database
                    if save_upload(
                        username, 
                        selected_date_str, 
                        category_info['name'],
                        uploaded_file.name,
                        int(file_size),
                        uploaded_file.type
                    ):
                        st.markdown(f"""
                        <div class="success-msg">
                            ✅ <strong>{uploaded_file.name}</strong> ({file_size:.1f} KB)<br/>
                            Type: {uploaded_file.type}
                        </div>
                        """, unsafe_allow_html=True)
    
    # Show uploaded files for the day
    st.markdown("---")
    st.markdown("### 📋 Today's Uploads")
    
    uploads = get_uploads(username, selected_date_str)
    
    if uploads:
        upload_df = pd.DataFrame(uploads, columns=['Category', 'Filename', 'Size (KB)', 'Type', 'Upload Time'])
        st.dataframe(upload_df, use_container_width=True, hide_index=True)
        
        st.success(f"✅ Total files uploaded today: {len(uploads)}")
    else:
        st.info("📝 No files uploaded yet for this date.")

# ============================================
# TAB 4: MANAGE RMS
# ============================================

def show_manage_rms():
    """Manage RM list"""
    
    st.markdown("# 👥 Manage Your RMs")
    st.markdown("---")
    
    username = st.session_state.current_user
    
    # Current RMs
    rms = get_user_rms(username)
    
    st.markdown(f"### Current RMs ({len(rms)})")
    
    if rms:
        for i, rm in enumerate(rms):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i+1}. {rm}**")
            with col2:
                if st.button("❌ Delete", key=f"del_{rm}"):
                    if delete_rm(username, rm):
                        st.success(f"Deleted {rm}")
                        st.rerun()
    else:
        st.info("No RMs added yet")
    
    # Add new RM
    st.markdown("---")
    st.markdown("### Add New RM")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_rm_name = st.text_input("RM Name", placeholder="Enter RM name")
    
    with col2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("➕ Add RM", use_container_width=True):
            if new_rm_name:
                if add_rm(username, new_rm_name):
                    st.success(f"Added {new_rm_name}")
                    st.rerun()
                else:
                    st.error("RM already exists or error occurred")

# ============================================
# TAB 5: TEAM PERFORMANCE
# ============================================

def show_team_performance():
    """Show team performance"""
    
    st.markdown("# 🏆 ALL TEAM PERFORMANCE")
    st.markdown("---")
    
    df = get_team_summary()
    
    if len(df) == 0 or df['Total_Pitches'].sum() == 0:
        st.info("📝 No team data available yet.")
        return
    
    # Summary metrics
    st.markdown("### 📊 OVERALL SUMMARY")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Total RMs", int(df['Total_RMs'].sum()))
    
    with col2:
        st.metric("📞 Total Pitches", int(df['Total_Pitches'].sum()))
    
    with col3:
        st.metric("📝 Total Registrations", int(df['Total_Registrations'].sum()))
    
    with col4:
        avg_conv = round((df['Total_Registrations'].sum() / df['Total_Pitches'].sum() * 100), 1) if df['Total_Pitches'].sum() > 0 else 0
        st.metric("💯 Avg Conversion", f"{avg_conv}%")
    
    with col5:
        st.metric("🎓 Total MC Regs", int(df['Total_Current_MC'].sum()))
    
    st.markdown("---")
    
    # Team comparison table
    st.markdown("### 📋 TEAM COMPARISON")
    
    display_df = df[['Team_Leader', 'Total_RMs', 'Total_WA_Audit', 'Total_Call_Audit', 'Total_Mocks', 'Total_SL_Calls', 'Total_Pitches', 'Total_Registrations', 'Conversion_Rate']].copy()
    display_df.columns = ['Team Leader', 'RMs', 'WA Audit', 'Call Audit', 'Mocks', 'SL Calls', 'Pitches', 'Registrations', 'Conversion %']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    st.markdown("---")
    st.markdown("### 📊 Performance Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Conversion rate comparison
        fig_conv = px.bar(
            df, 
            x='Team_Leader', 
            y='Conversion_Rate',
            title='Conversion Rate by Team',
            color='Conversion_Rate',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        fig_conv.update_layout(showlegend=False)
        st.plotly_chart(fig_conv, use_container_width=True)
    
    with col2:
        # Registrations comparison
        fig_reg = px.bar(
            df,
            x='Team_Leader',
            y='Total_Registrations',
            title='Total Registrations by Team',
            color='Total_Registrations',
            color_continuous_scale='Reds'
        )
        fig_reg.update_layout(showlegend=False)
        st.plotly_chart(fig_reg, use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    """Main application"""
    
    if not st.session_state.logged_in:
        show_login()
    else:
        show_sidebar()
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Daily Data Entry",
            "✅ Daily Checklist",
            "📁 Document Upload",
            "👥 Manage RMs",
            "🏆 Team Performance"
        ])
        
        with tab1:
            show_table_data_entry()
        
        with tab2:
            show_daily_checklist()
        
        with tab3:
            show_document_upload()
        
        with tab4:
            show_manage_rms()
        
        with tab5:
            show_team_performance()

if __name__ == "__main__":
    main()
