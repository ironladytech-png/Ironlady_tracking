"""
IRON LADY - STREAMLIT DASHBOARD WITH GOOGLE SHEETS INTEGRATION
Real-time sales performance tracking dashboard
Team Leaders: Ghazala, Megha, Afreen (Trainee), Soumya (Trainee)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Try to import Google Sheets libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
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

# Custom CSS for Iron Lady branding
st.markdown(f"""
<style>
    /* Main background */
    .main {{
        background-color: {IRONLADY_COLORS['accent']};
    }}
    
    /* Metrics styling */
    .stMetric {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {IRONLADY_COLORS['primary']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {IRONLADY_COLORS['secondary']};
        font-weight: 900;
    }}
    
    /* Buttons */
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
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: white;
    }}
    
    /* Dataframe */
    .dataframe {{
        border: 2px solid {IRONLADY_COLORS['primary']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# TEAM LEADERS - UPDATED NAMES
# ============================================

TEAM_LEADERS = ['Ghazala', 'Megha', 'Afreen', 'Soumya']

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

@st.cache_resource
def connect_to_google_sheets():
    """Connect to Google Sheets using Streamlit secrets"""
    if not GSHEETS_AVAILABLE:
        return None
    
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
        
    except KeyError:
        st.warning("⚠️ Google Sheets credentials not found in secrets")
        return None
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_sheet_data(sheet_id):
    """Fetch data from Google Sheets"""
    if not GSHEETS_AVAILABLE:
        return None
    
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
            
            # Get all values as records
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
        # Try to find the name column
        name_col = None
        for col in df.columns:
            col_upper = str(col).upper()
            if any(keyword in col_upper for keyword in ['RM', 'NAME', 'TEAM', 'LEADER', 'TL']):
                name_col = col
                break
        
        if not name_col:
            continue
        
        # Look for data for each team leader
        for _, row in df.iterrows():
            name = str(row.get(name_col, '')).strip()
            
            # Check if this is one of our team leaders
            if name in TEAM_LEADERS:
                # Initialize entry
                entry = {
                    'name': name,
                    'rms': 0,
                    'pitches_target': 0,
                    'pitches_actual': 0,
                    'reg_target': 0,
                    'reg_actual': 0,
                }
                
                # Extract RMs
                for col in ['Total RMs', 'RMs', 'RM Count', 'Number of RMs', 'Total RM']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['rms'] = int(val)
                            break
                
                # Extract Pitch Target
                for col in ['Target Pitch', 'Pitch Target', 'Target', 'Pitch Goal', 'Target Pitches']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['pitches_target'] = int(val)
                            break
                
                # Extract Pitch Actual
                for col in ['Actual Pitch', 'Pitch Actual', 'Achieved', 'Pitch Done', 'Pitches', 'Actual Pitches']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['pitches_actual'] = int(val)
                            break
                
                # Extract Registration Target
                for col in ['Target Registration', 'Registration Target', 'Target Reg', 'Reg Target', 'Target Registrations']:
                    if col in df.columns:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            entry['reg_target'] = int(val)
                            break
                
                # Extract Registration Actual
                for col in ['Actual Registration', 'Registration Actual', 'Actual Reg', 'Reg Done', 'Registrations', 'Actual Registrations']:
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
# SAMPLE DATA (FALLBACK)
# ============================================

def get_sample_data():
    """Sample data for Ghazala, Megha, Afreen, Soumya"""
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
    """Get status color based on percentage"""
    if percentage >= 90:
        return IRONLADY_COLORS['success']
    elif percentage >= 75:
        return IRONLADY_COLORS['warning']
    else:
        return IRONLADY_COLORS['danger']

def get_status_text(percentage):
    """Get status text based on percentage"""
    if percentage >= 90:
        return "Excellent 🎯"
    elif percentage >= 75:
        return "Good ✅"
    elif percentage >= 60:
        return "Fair ⚠️"
    else:
        return "Needs Attention ❌"

# ============================================
# MAIN DASHBOARD
# ============================================

def main():
    # Header with Iron Lady branding
    st.markdown(f"""
    <div style="text-align: center; padding: 50px 30px; background: {IRONLADY_COLORS['accent']}; border-top: 8px solid {IRONLADY_COLORS['primary']}; border-bottom: 8px solid {IRONLADY_COLORS['primary']}; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="font-size: 4rem; margin: 0; letter-spacing: 8px; color: {IRONLADY_COLORS['secondary']}; text-transform: uppercase;">IRON LADY</h1>
        <div style="background: {IRONLADY_COLORS['primary']}; height: 4px; width: 150px; margin: 20px auto;"></div>
        <p style="font-size: 1.3rem; margin: 0; color: {IRONLADY_COLORS['secondary']}; font-weight: 600;">Sales Performance Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_tl' not in st.session_state:
        st.session_state.selected_tl = None
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ DASHBOARD SETTINGS")
        
        st.markdown("---")
        st.markdown("### 📊 DATA SOURCE")
        
        use_sheets = st.checkbox("📈 Use Google Sheets (Live Data)", value=True)
        
        sheet_id = None
        if use_sheets:
            # Try to get from secrets first
            try:
                sheet_id = st.secrets.get("google_sheet_id", None)
                if sheet_id:
                    st.success("✅ Sheet ID configured")
                else:
                    sheet_id = st.text_input("Enter Google Sheet ID", placeholder="1abc123xyz...", help="Find this in your Google Sheets URL")
            except:
                sheet_id = st.text_input("Enter Google Sheet ID", placeholder="1abc123xyz...", help="Find this in your Google Sheets URL")
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Last updated timestamp
        st.info(f"**⏰ Last Updated**\n{datetime.now().strftime('%I:%M %p')}")
        
        st.markdown("---")
        
        # Team Leaders info
        st.markdown("### 👥 TEAM LEADERS")
        st.markdown("""
        🏆 **Ghazala** (Senior TL)  
        🏆 **Megha** (Senior TL)  
        🌟 **Afreen** (TL Trainee)  
        🌟 **Soumya** (TL Trainee)
        """)
        
        st.markdown("---")
        
        # Back to overview button
        if st.session_state.selected_tl:
            if st.button("⬅️ Back to Overview", use_container_width=True):
                st.session_state.selected_tl = None
                st.rerun()
    
    # Fetch Data from Google Sheets or use sample data
    team_data = None
    data_source = "📝 Sample Data (Demo Mode)"
    
    if use_sheets and sheet_id:
        with st.spinner("📊 Loading data from Google Sheets..."):
            sheet_data = fetch_sheet_data(sheet_id)
            if sheet_data:
                team_data = parse_team_data(sheet_data)
                if team_data:
                    data_source = "📊 Google Sheets (Live Data)"
                    st.success(f"✅ Successfully loaded data for {len(team_data)} team leaders")
                else:
                    st.warning("⚠️ No matching data found in Google Sheets. Using sample data.")
            else:
                st.warning("⚠️ Could not fetch Google Sheets data. Using sample data.")
    
    # Fallback to sample data if Google Sheets failed or not configured
    if not team_data:
        team_data = get_sample_data()
    
    # Convert to DataFrame
    df = pd.DataFrame(team_data)
    
    # Data Source Badge
    badge_color = '#d4edda' if 'Live' in data_source else '#fff3cd'
    st.markdown(f"""
    <div style="text-align: center; padding: 18px; background: {badge_color}; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <strong style="font-size: 1.1rem;">📊 Data Source:</strong> <span style="font-size: 1.1rem;">{data_source}</span><br>
        <strong style="font-size: 0.95rem;">🕐 Updated:</strong> <span style="font-size: 0.95rem;">{datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # INDIVIDUAL TL DASHBOARD
    # ============================================
    
    if st.session_state.selected_tl:
        # Individual TL Dashboard View
        tl_name = st.session_state.selected_tl
        tl_data = df[df['name'] == tl_name].iloc[0]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['primary']}; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="margin: 0; color: {IRONLADY_COLORS['primary']};">👤 {tl_name}'s Performance Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # TL Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💼 Relationship Managers",
                value=tl_data['rms'],
                help="Total number of RMs under supervision"
            )
        
        with col2:
            st.metric(
                label="🎯 Pitch Achievement",
                value=f"{tl_data['pitch_achievement']:.1f}%",
                delta=f"{tl_data['pitches_actual']}/{tl_data['pitches_target']}",
                help="Pitches completed vs target"
            )
        
        with col3:
            st.metric(
                label="📝 Registration Achievement",
                value=f"{tl_data['reg_achievement']:.1f}%",
                delta=f"{tl_data['reg_actual']}/{tl_data['reg_target']}",
                help="Registrations achieved vs target"
            )
        
        with col4:
            status = get_status_text(tl_data['conversion'])
            st.metric(
                label="💯 Conversion Rate",
                value=f"{tl_data['conversion']:.1f}%",
                delta=status,
                help="Registration rate from pitches"
            )
        
        st.markdown("---")
        
        # Performance Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Achievement Overview")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Pitch Achievement', 'Registration Achievement'],
                y=[tl_data['pitch_achievement'], tl_data['reg_achievement']],
                marker_color=[IRONLADY_COLORS['success'], IRONLADY_COLORS['warning']],
                text=[f"{tl_data['pitch_achievement']:.1f}%", f"{tl_data['reg_achievement']:.1f}%"],
                textposition='outside'
            ))
            fig.update_layout(
                height=400,
                yaxis_title='Achievement (%)',
                yaxis_range=[0, 110],
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Detailed Progress")
            progress_df = pd.DataFrame({
                'Metric': ['Pitches', 'Registrations'],
                'Target': [tl_data['pitches_target'], tl_data['reg_target']],
                'Actual': [tl_data['pitches_actual'], tl_data['reg_actual']],
                'Achievement': [f"{tl_data['pitch_achievement']:.1f}%", f"{tl_data['reg_achievement']:.1f}%"],
                'Gap': [
                    tl_data['pitches_target'] - tl_data['pitches_actual'],
                    tl_data['reg_target'] - tl_data['reg_actual']
                ]
            })
            st.dataframe(
                progress_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Target": st.column_config.NumberColumn("Target", width="small"),
                    "Actual": st.column_config.NumberColumn("Actual", width="small"),
                    "Achievement": st.column_config.TextColumn("Achievement %", width="medium"),
                    "Gap": st.column_config.NumberColumn("Gap", width="small"),
                }
            )
        
        st.markdown("---")
        
        # Performance Status
        conversion_color = get_status_color(tl_data['conversion'])
        st.markdown(f"""
        <div style="padding: 25px; background: {conversion_color}; color: white; border-radius: 12px; text-align: center; margin: 20px 0;">
            <h3 style="margin: 0; color: white;">Overall Performance Status</h3>
            <p style="margin: 10px 0 0 0; font-size: 1.5rem; font-weight: 900;">{get_status_text(tl_data['conversion'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # OVERVIEW DASHBOARD (TEAM SELECTION)
    # ============================================
    
    else:
        # Welcome message with team selection
        st.markdown(f"""
        <div style="padding: 25px; background: white; border-radius: 12px; border-left: 6px solid {IRONLADY_COLORS['warning']}; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: {IRONLADY_COLORS['secondary']};">👋 Welcome! Select your name to access your dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👥 TEAM LEADERS")
        
        # Create team leader selection buttons
        col1, col2 = st.columns(2)
        
        tl_list = TEAM_LEADERS
        
        for idx, tl in enumerate(tl_list):
            role = "Senior TL" if tl in ['Ghazala', 'Megha'] else "TL Trainee"
            icon = "🏆" if tl in ['Ghazala', 'Megha'] else "🌟"
            
            with col1 if idx % 2 == 0 else col2:
                button_html = f"""
                <div style="background: {IRONLADY_COLORS['primary']}; color: white; padding: 25px; text-align: center; font-size: 1.2rem; font-weight: 900; border-radius: 12px; cursor: pointer; margin: 15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;">
                    {icon} {tl.upper()}<br>
                    <span style="font-size: 0.8rem; font-weight: 400;">({role})</span>
                </div>
                """
                
                if st.button(f"{icon} {tl.upper()}", key=f"tl_{tl}", use_container_width=True, type="primary"):
                    st.session_state.selected_tl = tl
                    st.rerun()
        
        st.markdown("---")
        
        # Calculate overall team totals
        total_rms = df['rms'].sum()
        total_pitch_target = df['pitches_target'].sum()
        total_pitch_actual = df['pitches_actual'].sum()
        total_reg_target = df['reg_target'].sum()
        total_reg_actual = df['reg_actual'].sum()
        
        overall_pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
        overall_reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
        overall_conversion = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
        
        # Overall Team Metrics
        st.markdown("### 📊 OVERALL TEAM PERFORMANCE")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💼 Total RMs",
                value=total_rms,
                help="Total Relationship Managers across all teams"
            )
        
        with col2:
            st.metric(
                label="🎯 Pitch Achievement",
                value=f"{overall_pitch_achievement:.1f}%",
                delta=f"{total_pitch_actual}/{total_pitch_target}",
                help="Overall pitch completion rate"
            )
        
        with col3:
            st.metric(
                label="📝 Registration Achievement",
                value=f"{overall_reg_achievement:.1f}%",
                delta=f"{total_reg_actual}/{total_reg_target}",
                help="Overall registration completion rate"
            )
        
        with col4:
            st.metric(
                label="💯 Team Conversion Rate",
                value=f"{overall_conversion:.1f}%",
                delta=get_status_text(overall_conversion),
                help="Overall conversion from pitches to registrations"
            )
        
        st.markdown("---")
        
        # Detailed Team Performance Table
        st.markdown("### 📈 DETAILED TEAM PERFORMANCE")
        
        display_df = df.copy()
        display_df['Pitch Progress'] = display_df.apply(
            lambda x: f"{x['pitches_actual']}/{x['pitches_target']} ({x['pitch_achievement']:.1f}%)", axis=1
        )
        display_df['Reg Progress'] = display_df.apply(
            lambda x: f"{x['reg_actual']}/{x['reg_target']} ({x['reg_achievement']:.1f}%)", axis=1
        )
        display_df['Conversion'] = display_df['conversion'].apply(lambda x: f"{x:.1f}%")
        display_df['Status'] = display_df['conversion'].apply(get_status_text)
        
        table_df = display_df[['name', 'rms', 'Pitch Progress', 'Reg Progress', 'Conversion', 'Status']]
        table_df.columns = ['Team Leader', 'RMs', 'Pitches', 'Registrations', 'Conversion Rate', 'Status']
        
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
                "Status": st.column_config.TextColumn("Status", width="medium"),
            }
        )
        
        st.markdown("---")
        
        # Performance Comparison Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Conversion Rate Comparison")
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
            fig1.update_layout(showlegend=False, height=400, yaxis_range=[0, max(df['conversion']) + 10])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Achievement Comparison")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Pitch Achievement',
                x=df['name'],
                y=df['pitch_achievement'],
                marker_color=IRONLADY_COLORS['success'],
                text=df['pitch_achievement'],
                texttemplate='%{text:.1f}%',
                textposition='outside'
            ))
            fig2.add_trace(go.Bar(
                name='Registration Achievement',
                x=df['name'],
                y=df['reg_achievement'],
                marker_color=IRONLADY_COLORS['warning'],
                text=df['reg_achievement'],
                texttemplate='%{text:.1f}%',
                textposition='outside'
            ))
            fig2.update_layout(
                barmode='group',
                height=400,
                xaxis_title='Team Leader',
                yaxis_title='Achievement (%)',
                yaxis_range=[0, 110]
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Team Leaderboard
        st.markdown("### 🏆 PERFORMANCE LEADERBOARD")
        
        leaderboard_df = df.sort_values('conversion', ascending=False).copy()
        leaderboard_df['Rank'] = range(1, len(leaderboard_df) + 1)
        leaderboard_df['Medal'] = ['🥇', '🥈', '🥉', '📊'][:len(leaderboard_df)]
        
        leaderboard_display = leaderboard_df[['Rank', 'Medal', 'name', 'conversion']]
        leaderboard_display.columns = ['Rank', '', 'Team Leader', 'Conversion Rate (%)']
        
        st.dataframe(
            leaderboard_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "": st.column_config.TextColumn("", width="small"),
                "Team Leader": st.column_config.TextColumn("Team Leader", width="large"),
                "Conversion Rate (%)": st.column_config.NumberColumn("Conversion Rate (%)", format="%.1f", width="medium"),
            }
        )
    
    # ============================================
    # FOOTER
    # ============================================
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: {IRONLADY_COLORS['accent']}; border-radius: 12px; border-top: 4px solid {IRONLADY_COLORS['primary']}; border-bottom: 4px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p style="margin: 0; font-weight: 900; font-size: 1.8rem; color: {IRONLADY_COLORS['secondary']}; letter-spacing: 3px;">IRON LADY</p>
        <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 100px; margin: 15px auto;"></div>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; color: {IRONLADY_COLORS['secondary']}; font-weight: 600;">Sales Performance Management System</p>
        <p style="margin: 15px 0 0 0; font-size: 0.9rem; color: {IRONLADY_COLORS['secondary']}; opacity: 0.7;">
            Team Leaders: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟
        </p>
        <p style="margin: 10px 0 0 0; font-size: 0.8rem; color: {IRONLADY_COLORS['secondary']}; opacity: 0.6;">
            © 2024 Iron Lady. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()
