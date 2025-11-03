"""
IRON LADY - STREAMLIT DASHBOARD WITH GOOGLE SHEETS
Real-time sales performance tracking dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import gspread
from google.oauth2.service_account import Credentials

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
    }}
    h1, h2, h3 {{
        color: {IRONLADY_COLORS['secondary']};
        font-weight: 900;
    }}
    .css-1d391kg {{
        background-color: {IRONLADY_COLORS['primary']};
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
        # Get credentials from Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        
        # Create credentials
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        # Authorize and return client
        client = gspread.authorize(credentials)
        return client
        
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    try:
        client = connect_to_google_sheets()
        if not client:
            return None
        
        # Open spreadsheet by ID
        spreadsheet = client.open_by_key(sheet_id)
        
        data = {}
        
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        
        for worksheet in worksheets:
            sheet_name = worksheet.title
            
            # Get all values as dataframe
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
        # Look for relevant columns
        for col in df.columns:
            if 'RM' in col.upper() or 'NAME' in col.upper():
                name_col = col
                break
        else:
            continue
        
        for _, row in df.iterrows():
            name = str(row.get(name_col, '')).strip()
            
            # Check if this is a team leader
            if name in TEAM_LEADERS:
                entry = {
                    'name': name,
                    'rms': int(row.get('Total RMs', 0) or 0),
                    'pitches_target': int(row.get('Target Pitch', 0) or row.get('Target', 0) or 0),
                    'pitches_actual': int(row.get('Actual Pitch', 0) or row.get('Achieved', 0) or 0),
                    'reg_target': int(row.get('Target Registration', 0) or row.get('Target Reg', 0) or 0),
                    'reg_actual': int(row.get('Actual Registration', 0) or row.get('Actual Reg', 0) or 0),
                }
                
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
# SAMPLE DATA (FALLBACK)
# ============================================

def get_sample_data():
    """Sample data for demo/fallback"""
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
# MAIN DASHBOARD
# ============================================

def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: {IRONLADY_COLORS['accent']}; border-radius: 10px; border: 3px solid {IRONLADY_COLORS['primary']};">
            <h1 style="font-size: 3.5rem; margin: 0; letter-spacing: 5px;">IRON LADY</h1>
            <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Sales Performance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### ⚙️ SETTINGS")
        
        # Google Sheets Configuration
        st.markdown("---")
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox("Use Google Sheets", value=True)
        
        if use_sheets:
            # Get Sheet ID from secrets or user input
            if "google_sheet_id" in st.secrets:
                sheet_id = st.secrets["google_sheet_id"]
                st.success(f"✅ Connected to Sheet")
            else:
                sheet_id = st.text_input("Google Sheet ID", placeholder="1abc123xyz...")
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Last updated
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%I:%M %p')}")
        
        st.markdown("---")
        st.markdown("**Team Leaders:**")
        for tl in TEAM_LEADERS:
            st.markdown(f"• {tl}")
    
    # Fetch Data
    team_data = None
    data_source = "Sample Data"
    
    if use_sheets and sheet_id:
        with st.spinner("📊 Loading data from Google Sheets..."):
            sheet_data = fetch_sheet_data(sheet_id)
            if sheet_data:
                team_data = parse_team_data(sheet_data)
                if team_data:
                    data_source = "Google Sheets (Live)"
                    st.success("✅ Data loaded from Google Sheets")
    
    # Fallback to sample data
    if not team_data:
        team_data = get_sample_data()
        if use_sheets:
            st.warning("⚠️ Using sample data. Check Google Sheets connection.")
    
    # Convert to DataFrame
    df = pd.DataFrame(team_data)
    
    # Calculate totals
    total_rms = df['rms'].sum()
    total_pitch_target = df['pitches_target'].sum()
    total_pitch_actual = df['pitches_actual'].sum()
    total_reg_target = df['reg_target'].sum()
    total_reg_actual = df['reg_actual'].sum()
    
    overall_pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
    overall_reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
    overall_conversion = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
    
    # Data Source Badge
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: {'#d4edda' if data_source == 'Google Sheets (Live)' else '#fff3cd'}; border-radius: 5px; margin-bottom: 20px;">
        <strong>📊 Data Source:</strong> {data_source} | <strong>🕐 Updated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics Row
    st.markdown("### 📊 OVERALL PERFORMANCE")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💼 Total RMs",
            value=total_rms,
            delta=None
        )
    
    with col2:
        st.metric(
            label="🎯 Pitch Achievement",
            value=f"{overall_pitch_achievement}%",
            delta=f"{total_pitch_actual}/{total_pitch_target}"
        )
    
    with col3:
        st.metric(
            label="📝 Registration Achievement",
            value=f"{overall_reg_achievement}%",
            delta=f"{total_reg_actual}/{total_reg_target}"
        )
    
    with col4:
        st.metric(
            label="💯 Conversion Rate",
            value=f"{overall_conversion}%",
            delta="Good" if overall_conversion >= 75 else "Needs Improvement"
        )
    
    st.markdown("---")
    
    # Team Leader Performance Table
    st.markdown("### 👥 TEAM LEADER PERFORMANCE")
    
    # Format DataFrame for display
    display_df = df.copy()
    display_df['Pitch Progress'] = display_df.apply(
        lambda x: f"{x['pitches_actual']}/{x['pitches_target']} ({x['pitch_achievement']}%)", axis=1
    )
    display_df['Reg Progress'] = display_df.apply(
        lambda x: f"{x['reg_actual']}/{x['reg_target']} ({x['reg_achievement']}%)", axis=1
    )
    display_df['Conversion'] = display_df['conversion'].apply(lambda x: f"{x}%")
    
    # Select columns to display
    table_df = display_df[['name', 'rms', 'Pitch Progress', 'Reg Progress', 'Conversion']]
    table_df.columns = ['Team Leader', 'RMs', 'Pitches', 'Registrations', 'Conversion Rate']
    
    # Display styled table
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Team Leader": st.column_config.TextColumn("Team Leader", width="medium"),
            "RMs": st.column_config.NumberColumn("RMs", width="small"),
            "Pitches": st.column_config.TextColumn("Pitches", width="medium"),
            "Registrations": st.column_config.TextColumn("Registrations", width="medium"),
            "Conversion Rate": st.column_config.TextColumn("Conversion Rate", width="small"),
        }
    )
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Conversion Rate by Team Leader")
        fig1 = px.bar(
            df,
            x='name',
            y='conversion',
            color='conversion',
            color_continuous_scale=['#D62828', '#F77F00', '#2A9D8F'],
            labels={'name': 'Team Leader', 'conversion': 'Conversion Rate (%)'}
        )
        fig1.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Achievement Comparison")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Pitch Achievement',
            x=df['name'],
            y=df['pitch_achievement'],
            marker_color=IRONLADY_COLORS['success']
        ))
        fig2.add_trace(go.Bar(
            name='Registration Achievement',
            x=df['name'],
            y=df['reg_achievement'],
            marker_color=IRONLADY_COLORS['warning']
        ))
        fig2.update_layout(
            barmode='group',
            height=400,
            xaxis_title='Team Leader',
            yaxis_title='Achievement (%)'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: {IRONLADY_COLORS['accent']}; border-radius: 10px;">
        <p style="margin: 0; font-weight: 900; font-size: 1.2rem;">IRON LADY</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Sales Performance Management System</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
