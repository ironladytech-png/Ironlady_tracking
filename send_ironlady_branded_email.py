"""
IRON LADY - Email Script for Multiple Team Leader Worksheets
FIXED VERSION - Improved checklist status detection and multiple email recipients
Reads from separate worksheets: Ghazala, Afreen, Soumya, Sweksha, NJ - T&E
Handles Target/Achieved column pairs
Shows targets even when achieved values are empty
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# CONFIGURATION
# ============================================

# Email config
EMAIL_SENDER = os.getenv('GMAIL_USER', '').strip()
EMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '').strip()
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# Recipients - IMPROVED HANDLING
CEO_EMAIL = os.getenv('CEO_EMAIL', '').strip()
AUTO_MAIL = os.getenv('AUTO_MAIL', '').strip()

# Clean and parse recipients - handle multiple formats
def parse_email_recipients():
    """Parse email recipients from environment variables"""
    recipient_list = []
    
    # Combine all email sources
    all_emails = f"{CEO_EMAIL} {AUTO_MAIL}"
    
    # Remove all types of newlines and split by common separators
    all_emails = all_emails.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    all_emails = all_emails.replace(',', ' ').replace(';', ' ')
    
    # Split and clean
    for email in all_emails.split():
        email = email.strip()
        # Validate email format
        if email and '@' in email and '.' in email.split('@')[1]:
            recipient_list.append(email)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recipients = []
    for email in recipient_list:
        if email.lower() not in seen:
            seen.add(email.lower())
            unique_recipients.append(email)
    
    return unique_recipients

RECIPIENT_EMAILS = parse_email_recipients()

# Google Sheets config
SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '').strip()
CREDENTIALS_JSON = os.getenv('GOOGLE_SHEETS_CREDENTIALS', '').strip()

# Colors
IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
}

# Team Leader worksheets mapping - UPDATED
TEAM_LEADERS = {
    'Ghazala': 'Ghazala - Rising Stars',
    'Afreen': 'Afreen - High Flyers',
    'Soumya': 'Soumya - Goal Getters',
    'Sweksha': 'Sweksha - Team'
}

# ============================================
# GOOGLE SHEETS FUNCTIONS
# ============================================

def get_sheets_client():
    """Get authenticated Google Sheets client"""
    if not CREDENTIALS_JSON or not SHEET_ID:
        print("❌ Missing GOOGLE_SHEETS_CREDENTIALS or GOOGLE_SHEET_ID")
        return None
    
    try:
        credentials_dict = json.loads(CREDENTIALS_JSON)
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        client = gspread.authorize(credentials)
        print("✅ Google Sheets client authorized")
        return client
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return None

def find_date_row(worksheet, target_date):
    """Find the row that starts with the target date"""
    try:
        all_values = worksheet.get_all_values()
        
        # Look for date in first column
        for idx, row in enumerate(all_values):
            if row and len(row) > 0:
                cell_value = str(row[0]).strip()
                # Check if it matches the date format (Nov 13, Nov 12, etc.)
                if target_date in cell_value or cell_value == target_date:
                    return idx
        
        return None
    except Exception as e:
        print(f"⚠️  Error finding date row: {e}")
        return None

def parse_team_leader_sheet(worksheet, date_str):
    """
    Parse a team leader worksheet with structure:
    Date | Team Name | WA Audit (Target/Achieved) | Call Audit | Mocks | SL calls | Follow ups Registrations
           RM Name   | Target | Achieved | Target | Achieved | ...
    """
    try:
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 3:
            print(f"⚠️  Sheet too small: {len(all_values)} rows")
            return []
        
        # Find the date
        date_simple = datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d').lstrip('0')
        print(f"   Looking for date: {date_simple} or {date_str}")
        
        date_row_idx = None
        for idx, row in enumerate(all_values):
            if row and len(row) > 0:
                cell = str(row[0]).strip()
                if date_simple in cell or date_str in cell:
                    date_row_idx = idx
                    print(f"   Found date at row {idx}")
                    break
        
        if date_row_idx is None:
            print(f"   ❌ Date not found in sheet")
            return []
        
        # The header row should be right after the date
        # Usually: row with "RM Name", "Target", "Achieved", etc.
        header_row_idx = date_row_idx + 1
        
        # Data rows start after header
        data_start_idx = header_row_idx + 1
        
        # Read until we hit another date or empty rows
        rm_data = []
        seen_rms = set()  # Track RMs we've already added to prevent duplicates
        
        for idx in range(data_start_idx, len(all_values)):
            row = all_values[idx]
            
            # Stop if we hit an empty row
            if not row or len(row) < 2:
                break
            
            rm_name = str(row[1]).strip() if len(row) > 1 else ''
            
            # Stop conditions:
            # 1. Empty RM name
            # 2. RM name contains date indicators
            # 3. RM name is same as team name (indicates section header)
            # 4. RM name is "RM Name" (indicates header row)
            # 5. We've already seen this RM (duplicate)
            if (not rm_name or 
                rm_name == '' or 
                'Nov' in rm_name or 
                'Jan' in rm_name or
                'Dec' in rm_name or
                rm_name == 'RM Name' or
                'Rising Stars' in rm_name or
                'High Flyers' in rm_name or
                'Goal Getters' in rm_name or
                rm_name in seen_rms):
                break
            
            seen_rms.add(rm_name)
            
            # Parse the metrics (columns: RM Name, Target, Achieved, Target, Achieved, ...)
            # WA Audit: cols 2,3
            # Call Audit: cols 4,5
            # Mocks: cols 6,7
            # SL Calls: cols 8,9
            # Follow ups Registrations: cols 10,11
            
            def safe_int(val):
                try:
                    return int(float(str(val).strip())) if val and str(val).strip() else 0
                except:
                    return 0
            
            wa_audit_target = safe_int(row[2]) if len(row) > 2 else 0
            wa_audit_achieved = safe_int(row[3]) if len(row) > 3 else 0
            
            call_audit_target = safe_int(row[4]) if len(row) > 4 else 0
            call_audit_achieved = safe_int(row[5]) if len(row) > 5 else 0
            
            mocks_target = safe_int(row[6]) if len(row) > 6 else 0
            mocks_achieved = safe_int(row[7]) if len(row) > 7 else 0
            
            sl_calls_target = safe_int(row[8]) if len(row) > 8 else 0
            sl_calls_achieved = safe_int(row[9]) if len(row) > 9 else 0
            
            registrations_target = safe_int(row[10]) if len(row) > 10 else 0
            registrations_achieved = safe_int(row[11]) if len(row) > 11 else 0
            
            rm_data.append({
                'rm_name': rm_name,
                'wa_audit_target': wa_audit_target,
                'wa_audit_achieved': wa_audit_achieved,
                'call_audit_target': call_audit_target,
                'call_audit_achieved': call_audit_achieved,
                'mocks_target': mocks_target,
                'mocks_achieved': mocks_achieved,
                'sl_calls_target': sl_calls_target,
                'sl_calls_achieved': sl_calls_achieved,
                'registrations_target': registrations_target,
                'registrations_achieved': registrations_achieved
            })
        
        print(f"   Found {len(rm_data)} RMs")
        return rm_data
        
    except Exception as e:
        print(f"   ❌ Error parsing sheet: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_all_team_data(date_str):
    """Get data from all team leader worksheets"""
    try:
        client = get_sheets_client()
        if not client:
            return {}
        
        spreadsheet = client.open_by_key(SHEET_ID)
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
        
        # Get all worksheets
        all_worksheets = spreadsheet.worksheets()
        available_sheets = [ws.title for ws in all_worksheets]
        print(f"✅ Available worksheets: {available_sheets}")
        
        team_data = {}
        
        for sheet_name, display_name in TEAM_LEADERS.items():
            print(f"\n📋 Processing: {sheet_name}")
            
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                rm_data = parse_team_leader_sheet(worksheet, date_str)
                
                if rm_data:
                    team_data[sheet_name] = {
                        'display_name': display_name,
                        'rms': rm_data
                    }
                    print(f"   ✅ Loaded {len(rm_data)} RMs from {sheet_name}")
                else:
                    print(f"   ⚠️  No data found for {date_str}")
                    # Still add with empty data to show targets
                    team_data[sheet_name] = {
                        'display_name': display_name,
                        'rms': []
                    }
                    
            except gspread.exceptions.WorksheetNotFound:
                print(f"   ❌ Worksheet '{sheet_name}' not found")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return team_data
        
    except Exception as e:
        print(f"❌ Error getting team data: {e}")
        import traceback
        traceback.print_exc()
        return {}

def aggregate_team_summary(team_data):
    """Aggregate data across all teams"""
    summary = {}
    
    for team_name, team_info in team_data.items():
        rms = team_info['rms']
        display_name = team_info['display_name']
        
        total_rms = len(rms)
        
        # Calculate totals
        wa_audit_target = sum(rm['wa_audit_target'] for rm in rms)
        wa_audit_achieved = sum(rm['wa_audit_achieved'] for rm in rms)
        
        call_audit_target = sum(rm['call_audit_target'] for rm in rms)
        call_audit_achieved = sum(rm['call_audit_achieved'] for rm in rms)
        
        mocks_target = sum(rm['mocks_target'] for rm in rms)
        mocks_achieved = sum(rm['mocks_achieved'] for rm in rms)
        
        sl_calls_target = sum(rm['sl_calls_target'] for rm in rms)
        sl_calls_achieved = sum(rm['sl_calls_achieved'] for rm in rms)
        
        registrations_target = sum(rm['registrations_target'] for rm in rms)
        registrations_achieved = sum(rm['registrations_achieved'] for rm in rms)
        
        # Calculate conversion rate
        conversion_rate = 0.0
        if registrations_target > 0:
            conversion_rate = round((registrations_achieved / registrations_target * 100), 1)
        
        summary[team_name] = {
            'display_name': display_name,
            'total_rms': total_rms,
            'wa_audit_target': wa_audit_target,
            'wa_audit_achieved': wa_audit_achieved,
            'call_audit_target': call_audit_target,
            'call_audit_achieved': call_audit_achieved,
            'mocks_target': mocks_target,
            'mocks_achieved': mocks_achieved,
            'sl_calls_target': sl_calls_target,
            'sl_calls_achieved': sl_calls_achieved,
            'registrations_target': registrations_target,
            'registrations_achieved': registrations_achieved,
            'conversion_rate': conversion_rate
        }
    
    return summary

def get_checklist_status(date_str):
    """Get checklist completion status for each team leader - IMPROVED VERSION"""
    try:
        client = get_sheets_client()
        if not client:
            print("⚠️  Could not get sheets client for checklist")
            return {}
        
        spreadsheet = client.open_by_key(SHEET_ID)
        
        # Try to find the Checklists worksheet
        try:
            worksheet = spreadsheet.worksheet('Checklists')
            print("✅ Found Checklists worksheet")
        except gspread.exceptions.WorksheetNotFound:
            print("⚠️  'Checklists' worksheet not found")
            
            # Try alternative names
            all_sheets = [ws.title for ws in spreadsheet.worksheets()]
            print(f"   Available worksheets: {all_sheets}")
            
            # Look for worksheet with 'checklist' in name (case insensitive)
            checklist_sheet = None
            for sheet_name in all_sheets:
                if 'checklist' in sheet_name.lower():
                    try:
                        worksheet = spreadsheet.worksheet(sheet_name)
                        print(f"✅ Found alternative checklist worksheet: {sheet_name}")
                        checklist_sheet = worksheet
                        break
                    except:
                        continue
            
            if not checklist_sheet:
                print("❌ No checklist worksheet found")
                return {}
        
        # Get all data
        all_data = worksheet.get_all_values()
        print(f"   Retrieved {len(all_data)} rows from Checklists")
        
        if len(all_data) <= 1:
            print("⚠️  No data rows in Checklists worksheet")
            return {}
        
        # Show the headers for debugging
        headers = all_data[0]
        print(f"   Headers: {headers}")
        
        # Create DataFrame
        df = pd.DataFrame(all_data[1:], columns=headers)
        print(f"   Total checklist entries: {len(df)}")
        
        # Check what columns we have
        print(f"   Available columns: {df.columns.tolist()}")
        
        # Identify the username/name column
        username_col = None
        for col in ['Username', 'username', 'User', 'user', 'Name', 'name', 'Team_Leader', 'team_leader', 'TL', 'tl']:
            if col in df.columns:
                username_col = col
                print(f"   Using '{username_col}' as username column")
                break
        
        if not username_col:
            print("❌ Could not find username column in checklist data")
            return {}
        
        # Identify the completed column
        completed_col = None
        for col in ['Completed', 'completed', 'Status', 'status', 'Done', 'done', 'Complete', 'complete']:
            if col in df.columns:
                completed_col = col
                print(f"   Using '{completed_col}' as completed column")
                break
        
        # Check unique users
        unique_users = df[username_col].unique()
        print(f"   Users in checklist: {unique_users}")
        
        # Try different date matching strategies
        date_formats = [
            date_str,  # 2025-11-13
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d'),  # Nov 13
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y'),  # November 13, 2025
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%m/%d/%Y'),  # 11/13/2025
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y'),  # 13/11/2025
        ]
        
        filtered_df = pd.DataFrame()
        matched_date_format = None
        
        # Try to filter by date if Date column exists
        date_col = None
        for col in ['Date', 'date', 'Timestamp', 'timestamp', 'Day', 'day']:
            if col in df.columns:
                date_col = col
                print(f"   Using '{date_col}' as date column")
                break
        
        if date_col:
            for date_format in date_formats:
                filtered_df = df[df[date_col].str.contains(date_format, na=False, case=False)].copy()
                if len(filtered_df) > 0:
                    matched_date_format = date_format
                    print(f"   ✅ Found {len(filtered_df)} entries matching date: {date_format}")
                    break
        
        # If no matches, use all data (assume it's today's data)
        if len(filtered_df) == 0:
            print(f"   ⚠️ No date-specific data found, using all checklist data")
            filtered_df = df.copy()
        
        if len(filtered_df) == 0:
            print(f"   ❌ No checklist data after filtering")
            return {}
        
        # Aggregate by team leader with improved matching
        checklist_status = {}
        
        for team_name in TEAM_LEADERS.keys():
            team_lower = team_name.lower()
            
            # Try multiple matching strategies
            team_data = pd.DataFrame()
            
            # Strategy 1: Exact match (case insensitive)
            team_data = filtered_df[filtered_df[username_col].str.lower() == team_lower]
            
            # Strategy 2: Partial match (contains)
            if len(team_data) == 0:
                team_data = filtered_df[filtered_df[username_col].str.lower().str.contains(team_lower, na=False)]
            
            # Strategy 3: Match first name only
            if len(team_data) == 0:
                for user in unique_users:
                    if team_lower in str(user).lower():
                        team_data = filtered_df[filtered_df[username_col] == user]
                        print(f"   Matched '{team_name}' to user '{user}'")
                        break
            
            if len(team_data) > 0:
                total_tasks = len(team_data)
                
                # Check for completed tasks
                completed_tasks = 0
                if completed_col:
                    # Try different ways to identify completed tasks
                    completed_tasks = len(team_data[
                        (team_data[completed_col].str.upper() == 'TRUE') |
                        (team_data[completed_col].str.upper() == 'YES') |
                        (team_data[completed_col].str.upper() == 'Y') |
                        (team_data[completed_col] == '1') |
                        (team_data[completed_col].str.upper() == 'COMPLETE') |
                        (team_data[completed_col].str.upper() == 'DONE')
                    ])
                else:
                    print(f"   ⚠️ No completed column found, assuming 0 completed")
                
                # Get day type if available
                day_type = 'Unknown'
                if 'Day_Type' in team_data.columns:
                    day_type = team_data['Day_Type'].iloc[0]
                elif 'day_type' in team_data.columns:
                    day_type = team_data['day_type'].iloc[0]
                elif 'DayType' in team_data.columns:
                    day_type = team_data['DayType'].iloc[0]
                elif 'Type' in team_data.columns:
                    day_type = team_data['Type'].iloc[0]
                
                percentage = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
                
                checklist_status[team_name] = {
                    'day_type': day_type,
                    'completed': completed_tasks,
                    'total': total_tasks,
                    'percentage': percentage
                }
                
                print(f"   ✅ {team_name}: {completed_tasks}/{total_tasks} ({percentage}%) - {day_type}")
            else:
                print(f"   ⚠️ No checklist data found for {team_name}")
        
        if len(checklist_status) > 0:
            print(f"✅ Checklist status compiled for {len(checklist_status)} team leaders")
        else:
            print("❌ No checklist status data matched any team leaders")
            print(f"   Team leaders looking for: {list(TEAM_LEADERS.keys())}")
            print(f"   Usernames in data: {unique_users.tolist()}")
        
        return checklist_status
        
    except Exception as e:
        print(f"❌ Error getting checklist status: {e}")
        import traceback
        traceback.print_exc()
        return {}

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(team_summary, team_data, checklist_status={}):
    """Create HTML email with team and RM-level details"""
    
    # Calculate overall totals
    total_rms = sum(t['total_rms'] for t in team_summary.values())
    total_reg_target = sum(t['registrations_target'] for t in team_summary.values())
    total_reg_achieved = sum(t['registrations_achieved'] for t in team_summary.values())
    avg_conversion = round((total_reg_achieved / total_reg_target * 100), 1) if total_reg_target > 0 else 0
    
    # Team summary table
    team_rows = ""
    for team_name, data in team_summary.items():
        conv = data['conversion_rate']
        if conv >= 15:
            conv_color = IRONLADY_COLORS['success']
            conv_icon = '✅'
        elif conv >= 10:
            conv_color = IRONLADY_COLORS['primary']
            conv_icon = '⚠️'
        else:
            conv_color = '#dc3545'
            conv_icon = '❌'
        
        team_rows += f"""
        <tr>
            <td style="padding: 12px;"><strong>{data['display_name']}</strong></td>
            <td style="padding: 12px; text-align: center;">{data['total_rms']}</td>
            <td style="padding: 12px; text-align: center;">{data['registrations_target']}</td>
            <td style="padding: 12px; text-align: center;">{data['registrations_achieved']}</td>
            <td style="padding: 12px; text-align: center;">
                {conv_icon} <span style="color: {conv_color}; font-weight: 700;">{conv}%</span>
            </td>
        </tr>
        """
    
    # RM-level details for each team
    rm_details_html = ""
    for team_name, team_info in team_data.items():
        display_name = team_info['display_name']
        rms = team_info['rms']
        
        if not rms:
            continue
        
        rm_details_html += f"""
        <h3 style="color: {IRONLADY_COLORS['secondary']}; margin-top: 30px; padding: 10px; background: {IRONLADY_COLORS['accent']};">
            {display_name} - RM Details
        </h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 0.9rem;">
            <tr style="background: {IRONLADY_COLORS['secondary']}; color: white;">
                <th style="padding: 10px; text-align: left;">RM Name</th>
                <th style="padding: 10px; text-align: center;">WA Audit<br/><small>T/A</small></th>
                <th style="padding: 10px; text-align: center;">Call Audit<br/><small>T/A</small></th>
                <th style="padding: 10px; text-align: center;">Mocks<br/><small>T/A</small></th>
                <th style="padding: 10px; text-align: center;">SL Calls<br/><small>T/A</small></th>
                <th style="padding: 10px; text-align: center;">Registrations<br/><small>T/A</small></th>
            </tr>
        """
        
        for rm in rms:
            rm_details_html += f"""
            <tr>
                <td style="padding: 10px;">{rm['rm_name']}</td>
                <td style="padding: 10px; text-align: center;">{rm['wa_audit_target']}/{rm['wa_audit_achieved']}</td>
                <td style="padding: 10px; text-align: center;">{rm['call_audit_target']}/{rm['call_audit_achieved']}</td>
                <td style="padding: 10px; text-align: center;">{rm['mocks_target']}/{rm['mocks_achieved']}</td>
                <td style="padding: 10px; text-align: center;">{rm['sl_calls_target']}/{rm['sl_calls_achieved']}</td>
                <td style="padding: 10px; text-align: center;">{rm['registrations_target']}/{rm['registrations_achieved']}</td>
            </tr>
            """
        
        rm_details_html += "</table>"
    
    # Checklist status section - IMPROVED DISPLAY
    checklist_html = ""
    if checklist_status and len(checklist_status) > 0:
        checklist_html = f"""
        <h2 class="section-title">✅ Daily Checklist Status</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: {IRONLADY_COLORS['secondary']}; color: white;">
                <th style="padding: 12px; text-align: left;">Team Leader</th>
                <th style="padding: 12px; text-align: center;">Day Type</th>
                <th style="padding: 12px; text-align: center;">Completed</th>
                <th style="padding: 12px; text-align: center;">Total Tasks</th>
                <th style="padding: 12px; text-align: center;">Progress</th>
                <th style="padding: 12px; text-align: center;">Status</th>
            </tr>
        """
        
        for team_name, display_name in TEAM_LEADERS.items():
            if team_name in checklist_status:
                status = checklist_status[team_name]
                percentage = status['percentage']
                
                if percentage == 100:
                    status_icon = '✅'
                    status_text = 'Complete'
                    status_color = IRONLADY_COLORS['success']
                elif percentage >= 50:
                    status_icon = '⚠️'
                    status_text = 'In Progress'
                    status_color = IRONLADY_COLORS['primary']
                else:
                    status_icon = '❌'
                    status_text = 'Not Started'
                    status_color = '#dc3545'
                
                checklist_html += f"""
                <tr>
                    <td style="padding: 12px;"><strong>{display_name}</strong></td>
                    <td style="padding: 12px; text-align: center;">{status['day_type']}</td>
                    <td style="padding: 12px; text-align: center; font-weight: 700;">{status['completed']}</td>
                    <td style="padding: 12px; text-align: center;">{status['total']}</td>
                    <td style="padding: 12px; text-align: center;">
                        <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; display: inline-block; width: 100px;">
                            <div style="background: {status_color}; height: 100%; width: {percentage}%;"></div>
                        </div>
                        <span style="margin-left: 10px;">{percentage}%</span>
                    </td>
                    <td style="padding: 12px; text-align: center;">
                        {status_icon} <span style="color: {status_color}; font-weight: 700;">{status_text}</span>
                    </td>
                </tr>
                """
            else:
                checklist_html += f"""
                <tr>
                    <td style="padding: 12px;"><strong>{display_name}</strong></td>
                    <td style="padding: 12px; text-align: center;" colspan="5">
                        <span style="color: #999;">No checklist data</span>
                    </td>
                </tr>
                """
        
        checklist_html += "</table>"
    else:
        # Show message that checklist data is not available
        checklist_html = f"""
        <h2 class="section-title">✅ Daily Checklist Status</h2>
        <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; margin: 15px 0; border-left: 5px solid {IRONLADY_COLORS['primary']}; border-radius: 5px;">
            <p style="margin: 0; color: #666;">
                <strong>ℹ️ Checklist data not available</strong><br/>
                <small>Please ensure the 'Checklists' worksheet exists and contains data for today's date.</small>
            </p>
        </div>
        """
    
    # Complete HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: {IRONLADY_COLORS['accent']}; margin: 0; padding: 0; }}
            .container {{ max-width: 1000px; margin: 20px auto; background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
            .header {{ background: linear-gradient(135deg, {IRONLADY_COLORS['primary']} 0%, {IRONLADY_COLORS['secondary']} 100%); color: white; padding: 40px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 2.5rem; letter-spacing: 3px; font-weight: 900; }}
            .content {{ padding: 40px 30px; }}
            .section-title {{ color: {IRONLADY_COLORS['secondary']}; font-size: 1.5rem; font-weight: 900; margin: 30px 0 15px; padding-bottom: 10px; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; }}
            .metric {{ background: {IRONLADY_COLORS['accent']}; padding: 20px; margin: 15px 0; border-left: 5px solid {IRONLADY_COLORS['primary']}; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: {IRONLADY_COLORS['secondary']}; color: white; padding: 15px; font-weight: 700; }}
            td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
            .highlight {{ background: {IRONLADY_COLORS['primary']}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: 700; }}
            .footer {{ background: {IRONLADY_COLORS['secondary']}; color: white; text-align: center; padding: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>IRON LADY</h1>
                <p>Daily Performance Report</p>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            <div class="content">
                <h2 class="section-title">📊 Executive Summary</h2>
                <div class="metric">
                    <strong>Total RMs:</strong> {total_rms}<br/>
                    <strong>Registration Target:</strong> {total_reg_target}<br/>
                    <strong>Registrations Achieved:</strong> {total_reg_achieved}<br/>
                    <strong>Achievement Rate:</strong> <span class="highlight">{avg_conversion}%</span>
                </div>
                
                <h2 class="section-title">🏆 Team Leader Performance</h2>
                <table>
                    <tr>
                        <th>Team Leader</th>
                        <th style="text-align: center;">RMs</th>
                        <th style="text-align: center;">Reg Target</th>
                        <th style="text-align: center;">Reg Achieved</th>
                        <th style="text-align: center;">Achievement %</th>
                    </tr>
                    {team_rows}
                </table>
                
                <h2 class="section-title">📋 RM-Level Details</h2>
                <p style="font-size: 0.9rem; color: #666;"><em>T/A = Target / Achieved</em></p>
                {rm_details_html}
                
                {checklist_html}
                
                <h2 class="section-title">💡 Key Insights</h2>
                <div class="metric">
                    {'✅ <strong>Excellent!</strong> Team meeting targets.' if avg_conversion >= 80 else '⚠️ <strong>Action needed:</strong> Below target achievement.'}
                </div>
            </div>
            <div class="footer">
                <p style="font-size: 1.3rem; font-weight: 900;">IRON LADY</p>
                <p>© 2024 Iron Lady. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(recipients, subject, html_body):
    """Send email to multiple recipients"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "Success"
    except Exception as e:
        return False, str(e)

# ============================================
# MAIN
# ============================================

def main():
    print("🚀 Iron Lady Email Automation - FIXED VERSION")
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("\n" + "="*60)
    print("CONFIGURATION CHECK")
    print("="*60)
    
    print(f"Gmail: {'✅' if EMAIL_SENDER else '❌'} {EMAIL_SENDER if EMAIL_SENDER else 'Not set'}")
    print(f"Password: {'✅' if EMAIL_PASSWORD else '❌'}")
    print(f"Recipients: {'✅' if RECIPIENT_EMAILS else '❌'} {len(RECIPIENT_EMAILS)} email(s)")
    if RECIPIENT_EMAILS:
        for email in RECIPIENT_EMAILS:
            print(f"  → {email}")
    else:
        print("  ⚠️  No recipients configured")
        print("  Set CEO_EMAIL and/or AUTO_MAIL environment variables")
        print("  Format: single email or multiple emails separated by commas/spaces/newlines")
    print(f"Sheet ID: {'✅' if SHEET_ID else '❌'}")
    print(f"Credentials: {'✅' if CREDENTIALS_JSON else '❌'}")
    
    if not all([SHEET_ID, CREDENTIALS_JSON]):
        print("\n❌ Missing required configuration!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("FETCHING DATA FROM GOOGLE SHEETS")
    print("="*60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Looking for data with date: {today}")
    
    # Get all team data
    team_data = get_all_team_data(today)
    
    if not team_data:
        print(f"\n❌ No team data found!")
        sys.exit(1)
    
    # Aggregate summary
    team_summary = aggregate_team_summary(team_data)
    
    print("\n" + "="*60)
    print("TEAM SUMMARY")
    print("="*60)
    
    for team_name, summary in team_summary.items():
        print(f"\n{summary['display_name']}:")
        print(f"  RMs: {summary['total_rms']}")
        print(f"  Registrations: {summary['registrations_achieved']}/{summary['registrations_target']} ({summary['conversion_rate']}%)")
    
    # Get checklist status with improved error handling
    print("\n" + "="*60)
    print("FETCHING CHECKLIST STATUS")
    print("="*60)
    
    checklist_status = get_checklist_status(today)
    if checklist_status and len(checklist_status) > 0:
        print(f"✅ Checklist data: {len(checklist_status)} team leaders")
        for team_name, status in checklist_status.items():
            print(f"  → {team_name}: {status['completed']}/{status['total']} ({status['percentage']}%) - {status['day_type']}")
    else:
        print("ℹ️  No checklist data found (this section will show as 'not available' in email)")
    
    # Create and send email
    if not RECIPIENT_EMAILS:
        print("\n⚠️  No recipients configured - generating email preview only")
        html_body = create_email_html(team_summary, team_data, checklist_status)
        
        with open('email_preview.html', 'w') as f:
            f.write(html_body)
        print("✅ Email preview saved to email_preview.html")
        return
    
    print("\n" + "="*60)
    print("SENDING EMAIL")
    print("="*60)
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(team_summary, team_data, checklist_status)
    
    success, message = send_email(RECIPIENT_EMAILS, subject, html_body)
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS!")
        print("="*60)
        print(f"📧 Email sent to {len(RECIPIENT_EMAILS)} recipients")
        for email in RECIPIENT_EMAILS:
            print(f"  ✓ {email}")
    else:
        print("❌ FAILED!")
        print("="*60)
        print(f"Error: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
