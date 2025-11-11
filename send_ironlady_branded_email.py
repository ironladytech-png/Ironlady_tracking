"""
IRON LADY - Email Automation Script for GitHub Actions
FIXED: Reads your actual Google Sheets structure with multiple tabs
Uses your existing secret names: GMAIL_USER, GMAIL_APP_PASSWORD, CEO_EMAIL, AUTO_MAIL
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys
import json
import re

# ============================================
# CONFIGURATION - USING YOUR SECRET NAMES
# ============================================

# Email configuration - using YOUR existing secret names
EMAIL_SENDER = os.getenv('GMAIL_USER', '').strip()
EMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '').strip()
EMAIL_SMTP_SERVER = 'smtp.gmail.com'  # Fixed for Gmail
EMAIL_SMTP_PORT = 587  # Fixed for Gmail

# Recipients - using YOUR secret names
CEO_EMAIL = os.getenv('CEO_EMAIL', '').strip()
AUTO_MAIL = os.getenv('AUTO_MAIL', '').strip()

# Clean and combine all recipient emails (handle newlines, commas, spaces)
recipient_list = []

if CEO_EMAIL:
    # Replace newlines and multiple spaces with single space
    cleaned = CEO_EMAIL.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # Split by comma and/or whitespace
    emails = [email.strip() for email in cleaned.replace(',', ' ').split() if email.strip() and '@' in email]
    recipient_list.extend(emails)

if AUTO_MAIL:
    # Replace newlines and multiple spaces with single space
    cleaned = AUTO_MAIL.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # Split by comma and/or whitespace
    emails = [email.strip() for email in cleaned.replace(',', ' ').split() if email.strip() and '@' in email]
    recipient_list.extend(emails)

# Remove duplicates and invalid emails
RECIPIENT_EMAILS = list(set([email for email in recipient_list if email and '@' in email and '.' in email]))

# Iron Lady Colors
IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
}

# ============================================
# CHECKLIST & UPLOAD DATA
# ============================================

def get_checklist_status():
    """
    Get checklist completion status for each team leader
    Returns dict: {username: {'day_type': 'Day 1-1', 'completed': 15, 'total': 20, 'percentage': 75}}
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
        
        if not credentials_json or not sheet_id:
            return {}
        
        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to find a "Checklists" worksheet
        try:
            worksheet = spreadsheet.worksheet("Checklists")
            data = worksheet.get_all_records()
            
            if not data:
                return {}
            
            df = pd.DataFrame(data)
            
            # Aggregate by username
            checklist_status = {}
            
            for username in df['Username'].unique():
                user_data = df[df['Username'] == username]
                total_tasks = len(user_data)
                completed_tasks = len(user_data[user_data['Completed'] == True])
                day_type = user_data['Day_Type'].iloc[0] if len(user_data) > 0 else 'Unknown'
                
                checklist_status[username] = {
                    'day_type': day_type,
                    'completed': completed_tasks,
                    'total': total_tasks,
                    'percentage': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
                }
            
            return checklist_status
        
        except:
            # No Checklists worksheet found
            return {}
    
    except Exception as e:
        print(f"⚠️ Could not fetch checklist data: {e}")
        return {}

def get_upload_status():
    """
    Get document upload status for each team leader
    Returns dict: {username: {'total_files': 5, 'categories': ['WA Audit', 'Call Recording'], 'latest': '2024-11-07'}}
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
        
        if not credentials_json or not sheet_id:
            return {}
        
        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to find an "Uploads" worksheet
        try:
            worksheet = spreadsheet.worksheet("Uploads")
            data = worksheet.get_all_records()
            
            if not data:
                return {}
            
            df = pd.DataFrame(data)
            
            # Aggregate by username
            upload_status = {}
            
            for username in df['Username'].unique():
                user_data = df[df['Username'] == username]
                total_files = len(user_data)
                categories = user_data['Category'].unique().tolist()
                latest = user_data['Upload_Time'].max() if 'Upload_Time' in user_data.columns else 'Unknown'
                
                upload_status[username] = {
                    'total_files': total_files,
                    'categories': categories,
                    'latest': latest
                }
            
            return upload_status
        
        except:
            # No Uploads worksheet found
            return {}
    
    except Exception as e:
        print(f"⚠️ Could not fetch upload data: {e}")
        return {}

# ============================================
# GOOGLE SHEETS CONNECTION - FIXED FOR YOUR STRUCTURE
# ============================================

def parse_team_sheet(worksheet):
    """Parse a team leader's worksheet with your actual structure"""
    try:
        all_data = worksheet.get_all_values()
        
        # Find the team leader name from the sheet
        team_name = None
        for row in all_data[:10]:
            if len(row) > 1 and row[1] and ('-' in row[1] or 'Rising' in row[1] or 'Winners' in row[1] or 'Flyers' in row[1] or 'Getters' in row[1]):
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
                if len(row) > 3 and row[3] and row[3].strip() and row[3].strip().replace('-', '').isdigit():
                    total_wa_audit += abs(int(row[3]))
                
                # Call Audit Achieved (column F, index 5)
                if len(row) > 5 and row[5] and row[5].strip() and row[5].strip().replace('-', '').isdigit():
                    total_call_audit += abs(int(row[5]))
                
                # Mocks Achieved (column H, index 7)
                if len(row) > 7 and row[7] and row[7].strip() and row[7].strip().replace('-', '').isdigit():
                    total_mocks += abs(int(row[7]))
                
                # SL Calls Achieved (column J, index 9)
                if len(row) > 9 and row[9] and row[9].strip() and row[9].strip().replace('-', '').isdigit():
                    total_sl_calls += abs(int(row[9]))
                
                # Follow ups Registrations Achieved (column L, index 11)
                if len(row) > 11 and row[11] and row[11].strip():
                    val = row[11].strip()
                    # Extract number even if it has text (like "1-Shwetha")
                    num = re.findall(r'\d+', val)
                    if num:
                        total_registrations += int(num[0])
                
                # Pitches Achieved (column N, index 13)
                if len(row) > 13 and row[13] and row[13].strip() and row[13].strip().replace('-', '').isdigit():
                    total_pitches += abs(int(row[13]))
                
                # Current MC Registrations Achieved (column P, index 15)
                if len(row) > 15 and row[15] and row[15].strip() and row[15].strip().replace('-', '').isdigit():
                    total_current_mc += abs(int(row[15]))
                
                # Count this RM if they have any data
                if any([row[3], row[5], row[7], row[9], row[11], row[13], row[15]]):
                    rm_count += 1
            except:
                continue
        
        # Calculate conversion rate
        conversion_rate = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0.0
        
        return {
            'Team_Leader': team_name if team_name else 'Unknown',
            'Total_RMs': rm_count,
            'Total_WA_Audit': total_wa_audit,
            'Total_Call_Audit': total_call_audit,
            'Total_Mocks': total_mocks,
            'Total_SL_Calls': total_sl_calls,
            'Total_Pitches': total_pitches,
            'Total_Registrations': total_registrations,
            'Total_Current_MC': total_current_mc,
            'Conversion_Rate': conversion_rate
        }
    
    except Exception as e:
        print(f"⚠️ Error parsing sheet: {e}")
        return None

def get_data_from_sheets():
    """
    Fetch data from YOUR actual Google Sheets structure
    Reads all team sheets (Ghazala, Megha, Afreen, Soumya)
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Get credentials from environment
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
        
        if not credentials_json:
            print("⚠️ GOOGLE_SHEETS_CREDENTIALS not set")
            return None
        
        if not sheet_id:
            print("⚠️ GOOGLE_SHEET_ID not set")
            return None
        
        # Parse JSON credentials
        credentials_dict = json.loads(credentials_json)
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        client = gspread.authorize(credentials)
        
        print(f"📊 Connecting to Google Sheet: {sheet_id}")
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        print(f"📋 Found {len(worksheets)} worksheets")
        
        # Map worksheet names to team leaders
        sheet_mapping = {
            'Ghazala': 'ghazala',
            'Megha': 'megha',
            'Afreen': 'afreen',
            'Soumya': 'soumya'
        }
        
        team_data = []
        
        # Parse each team leader's sheet
        for worksheet in worksheets:
            sheet_title = worksheet.title
            print(f"   Checking sheet: {sheet_title}")
            
            # Find matching team leader
            matched = False
            for sheet_name in sheet_mapping.keys():
                if sheet_name.lower() in sheet_title.lower():
                    print(f"      ✓ Matched as {sheet_name}")
                    
                    # Parse the sheet
                    data = parse_team_sheet(worksheet)
                    
                    if data and data['Total_Pitches'] > 0:
                        team_data.append(data)
                        print(f"      ✓ Loaded data: {data['Total_Pitches']} pitches, {data['Total_Registrations']} registrations")
                    else:
                        print(f"      ⚠️ No data found in sheet")
                    
                    matched = True
                    break
            
            if not matched:
                print(f"      - Skipped (not a team leader sheet)")
        
        if not team_data:
            print("⚠️ No team data found in any sheets")
            return None
        
        print(f"✅ Loaded data from {len(team_data)} team sheets")
        df = pd.DataFrame(team_data)
        
        return df
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid GOOGLE_SHEETS_CREDENTIALS JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(df, checklist_status={}, upload_status={}):
    """Create HTML email with Iron Lady branding including checklist and upload status"""
    
    # Calculate totals
    total_rms = int(df['Total_RMs'].sum())
    total_pitches = int(df['Total_Pitches'].sum())
    total_registrations = int(df['Total_Registrations'].sum())
    avg_conversion = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0
    
    total_wa_audit = int(df['Total_WA_Audit'].sum()) if 'Total_WA_Audit' in df.columns else 0
    total_call_audit = int(df['Total_Call_Audit'].sum()) if 'Total_Call_Audit' in df.columns else 0
    total_mocks = int(df['Total_Mocks'].sum()) if 'Total_Mocks' in df.columns else 0
    total_sl_calls = int(df['Total_SL_Calls'].sum()) if 'Total_SL_Calls' in df.columns else 0
    total_current_mc = int(df['Total_Current_MC'].sum()) if 'Total_Current_MC' in df.columns else 0
    
    # Create table rows for team performance
    table_rows = ""
    for _, row in df.iterrows():
        conversion = row.get('Conversion_Rate', 0)
        table_rows += f"""
        <tr>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0;">{row['Team_Leader']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_RMs']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Pitches']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Registrations']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: 700;">{conversion}%</td>
        </tr>
        """
    
    # Create checklist status section
    checklist_html = ""
    if checklist_status:
        checklist_html = f"""
                <h2 class="section-title">✅ Daily Checklist Status</h2>
                <div style="background: white; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: left;">Team Leader</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Day Type</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Completed</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Progress</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Map usernames to team leader names
        username_map = {
            'ghazala': 'Ghazala - Rising Stars',
            'megha': 'Megha - Winners',
            'afreen': 'Afreen - High Flyers',
            'soumya': 'Soumya - Goal Getters'
        }
        
        for username, status in checklist_status.items():
            team_name = username_map.get(username, username.capitalize())
            percentage = status['percentage']
            status_icon = '✅' if percentage == 100 else '⚠️' if percentage >= 50 else '❌'
            status_text = 'Complete' if percentage == 100 else 'In Progress' if percentage > 0 else 'Not Started'
            status_color = IRONLADY_COLORS['success'] if percentage == 100 else IRONLADY_COLORS['primary'] if percentage >= 50 else '#dc3545'
            
            checklist_html += f"""
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{team_name}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{status['day_type']}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{status['completed']}/{status['total']}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
                                    <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                                        <div style="background: {status_color}; height: 100%; width: {percentage}%;"></div>
                                    </div>
                                </td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
                                    {status_icon} <span style="color: {status_color}; font-weight: 700;">{status_text}</span>
                                </td>
                            </tr>
            """
        
        checklist_html += """
                        </tbody>
                    </table>
                </div>
        """
    else:
        checklist_html = f"""
                <h2 class="section-title">✅ Daily Checklist Status</h2>
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
                    <p style="margin: 0;">ℹ️ No checklist data available. Team leaders should complete their daily checklists in the app.</p>
                </div>
        """
    
    # Create upload status section
    upload_html = ""
    if upload_status:
        upload_html = f"""
                <h2 class="section-title">📤 Document Upload Status</h2>
                <div style="background: white; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: left;">Team Leader</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Total Files</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: left;">Categories</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Latest Upload</th>
                                <th style="background: {IRONLADY_COLORS['secondary']}; color: white; padding: 12px; text-align: center;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Map usernames to team leader names
        username_map = {
            'ghazala': 'Ghazala - Rising Stars',
            'megha': 'Megha - Winners',
            'afreen': 'Afreen - High Flyers',
            'soumya': 'Soumya - Goal Getters'
        }
        
        for username, status in upload_status.items():
            team_name = username_map.get(username, username.capitalize())
            total_files = status['total_files']
            categories = ', '.join(status['categories'][:3])  # Show first 3 categories
            if len(status['categories']) > 3:
                categories += f" (+{len(status['categories']) - 3} more)"
            latest = status['latest']
            status_icon = '✅' if total_files > 0 else '❌'
            status_text = f'{total_files} uploaded' if total_files > 0 else 'No uploads'
            status_color = IRONLADY_COLORS['success'] if total_files > 0 else '#dc3545'
            
            upload_html += f"""
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{team_name}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: 700;">{total_files}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><small>{categories}</small></td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;"><small>{latest}</small></td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
                                    {status_icon} <span style="color: {status_color}; font-weight: 700;">{status_text}</span>
                                </td>
                            </tr>
            """
        
        upload_html += """
                        </tbody>
                    </table>
                </div>
        """
    else:
        upload_html = f"""
                <h2 class="section-title">📤 Document Upload Status</h2>
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
                    <p style="margin: 0;">ℹ️ No upload data available. Team leaders should upload required documents in the app.</p>
                </div>
        """
    
    # Create HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: {IRONLADY_COLORS['accent']};
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 900px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .header {{
                background: linear-gradient(135deg, {IRONLADY_COLORS['primary']} 0%, {IRONLADY_COLORS['secondary']} 100%);
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
                background: {IRONLADY_COLORS['accent']};
                padding: 20px;
                margin: 15px 0;
                border-left: 5px solid {IRONLADY_COLORS['primary']};
                border-radius: 5px;
            }}
            .section-title {{
                color: {IRONLADY_COLORS['secondary']};
                font-size: 1.5rem;
                font-weight: 900;
                margin: 30px 0 15px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid {IRONLADY_COLORS['primary']};
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th {{
                background: {IRONLADY_COLORS['secondary']};
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 700;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #e0e0e0;
            }}
            tr:hover {{
                background-color: {IRONLADY_COLORS['accent']};
            }}
            .footer {{
                background: {IRONLADY_COLORS['secondary']};
                color: white;
                text-align: center;
                padding: 30px;
            }}
            .highlight {{
                background: {IRONLADY_COLORS['primary']};
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
                <p>Daily Sales Performance Report</p>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            <div class="content">
                <h2 class="section-title">📊 Executive Summary</h2>
                <div class="metric">
                    <strong>Total RMs:</strong> {total_rms}<br/>
                    <strong>Total Pitches:</strong> {total_pitches}<br/>
                    <strong>Total Registrations:</strong> {total_registrations}<br/>
                    <strong>Average Conversion:</strong> <span class="highlight">{avg_conversion}%</span>
                </div>
                
                <h2 class="section-title">📋 Activity Summary</h2>
                <div class="metric">
                    <strong>WA Audit:</strong> {total_wa_audit}<br/>
                    <strong>Call Audit:</strong> {total_call_audit}<br/>
                    <strong>Mocks:</strong> {total_mocks}<br/>
                    <strong>SL Calls:</strong> {total_sl_calls}<br/>
                    <strong>Current MC Registrations:</strong> {total_current_mc}
                </div>
                
                <h2 class="section-title">🏆 Team Leader Performance</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Team Leader</th>
                            <th style="text-align: center;">Total RMs</th>
                            <th style="text-align: center;">Pitches</th>
                            <th style="text-align: center;">Registrations</th>
                            <th style="text-align: center;">Conversion %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                
                {checklist_html}
                
                {upload_html}
                
                <h2 class="section-title">💡 Key Insights</h2>
                <div class="metric">
                    {'✅ <strong>Excellent performance!</strong> Team is meeting conversion targets.' if avg_conversion >= 15 else '⚠️ <strong>Action needed:</strong> Team conversion below 15% target.'}
                </div>
            </div>
            <div class="footer">
                <p style="font-size: 1.3rem; font-weight: 900;">IRON LADY</p>
                <p>Team: Ghazala 🏆 | Megha 🏆 | Afreen 🌟 | Soumya 🌟</p>
                <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">
                    © 2024 Iron Lady. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(recipient_emails, subject, html_body):
    """Send email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = ', '.join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
        msg['Subject'] = subject
        
        # Attach HTML
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully"
    
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    """Main function to run email automation"""
    
    print("🚀 Iron Lady Email Automation Starting...")
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("\n" + "="*60)
    print("⚙️  CONFIGURATION CHECK")
    print("="*60)
    print(f"📧 GMAIL_USER (sender): {'✅ Set' if EMAIL_SENDER else '❌ Missing'}")
    if EMAIL_SENDER:
        print(f"   → {EMAIL_SENDER}")
    print(f"🔑 GMAIL_APP_PASSWORD: {'✅ Set' if EMAIL_PASSWORD else '❌ Missing'}")
    if EMAIL_PASSWORD:
        print(f"   → {'*' * len(EMAIL_PASSWORD)} (hidden)")
    print(f"📬 CEO_EMAIL: {'✅ Set' if CEO_EMAIL else '❌ Missing'}")
    if CEO_EMAIL:
        print(f"   → {CEO_EMAIL}")
    print(f"📬 AUTO_MAIL: {'✅ Set' if AUTO_MAIL else '❌ Missing'}")
    if AUTO_MAIL:
        print(f"   → {AUTO_MAIL}")
    print(f"📮 Combined Recipients: {'✅ ' + str(len(RECIPIENT_EMAILS)) + ' email(s)' if RECIPIENT_EMAILS else '❌ None'}")
    if RECIPIENT_EMAILS:
        for email in RECIPIENT_EMAILS:
            print(f"   → {email}")
    print(f"🌐 SMTP Server: {EMAIL_SMTP_SERVER}:{EMAIL_SMTP_PORT}")
    print("="*60)
    
    # Validate configuration
    errors = []
    
    if not EMAIL_SENDER:
        errors.append("❌ GMAIL_USER not set")
    
    if not EMAIL_PASSWORD:
        errors.append("❌ GMAIL_APP_PASSWORD not set")
    
    if not RECIPIENT_EMAILS:
        errors.append("❌ No recipient emails (CEO_EMAIL or AUTO_MAIL)")
    
    if errors:
        print("\n🚨 CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 SOLUTIONS:")
        print("   1. Go to: Settings → Secrets and variables → Actions")
        print("   2. Make sure these secrets are set:")
        print("      - GMAIL_USER (your Gmail address)")
        print("      - GMAIL_APP_PASSWORD (16-char app password)")
        print("      - CEO_EMAIL or AUTO_MAIL (recipient email addresses)")
        sys.exit(1)
    
    print("\n✅ All configuration validated!")
    
    # Get data
    print("\n" + "="*60)
    print("📊 FETCHING DATA FROM GOOGLE SHEETS")
    print("="*60)
    
    df = get_data_from_sheets()
    
    if df is None or len(df) == 0:
        print("\n❌ NO DATA AVAILABLE!")
        print("\n💡 SOLUTIONS:")
        print("   1. Make sure GOOGLE_SHEETS_CREDENTIALS is set (full JSON)")
        print("   2. Make sure GOOGLE_SHEET_ID is set")
        print("   3. Verify your Google Sheet has data in team tabs")
        print("   4. Expected tabs: Ghazala, Megha, Afreen, Soumya")
        print("   5. Share your sheet with the service account email")
        sys.exit(1)
    
    print(f"✅ Data ready: {len(df)} team leaders")
    print(f"📋 Team Leaders: {', '.join(df['Team_Leader'].tolist())}")
    
    # Get checklist status
    print("\n" + "="*60)
    print("✅ FETCHING CHECKLIST STATUS")
    print("="*60)
    
    checklist_status = get_checklist_status()
    if checklist_status:
        print(f"✅ Checklist data loaded for {len(checklist_status)} team leaders")
        for username, status in checklist_status.items():
            print(f"   → {username}: {status['completed']}/{status['total']} tasks ({status['percentage']}%)")
    else:
        print("ℹ️  No checklist data found (this is optional)")
    
    # Get upload status
    print("\n" + "="*60)
    print("📤 FETCHING UPLOAD STATUS")
    print("="*60)
    
    upload_status = get_upload_status()
    if upload_status:
        print(f"✅ Upload data loaded for {len(upload_status)} team leaders")
        for username, status in upload_status.items():
            print(f"   → {username}: {status['total_files']} files uploaded")
    else:
        print("ℹ️  No upload data found (this is optional)")
    
    # Create email
    print("\n" + "="*60)
    print("📝 CREATING EMAIL")
    print("="*60)
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    
    html_body = create_email_html(df, checklist_status, upload_status)
    print("✅ Email HTML created with all data from Google Sheets")
    if checklist_status:
        print("   ✓ Includes checklist completion status")
    if upload_status:
        print("   ✓ Includes document upload status")
    
    # Send email
    print("\n" + "="*60)
    print("📤 SENDING EMAIL")
    print("="*60)
    print(f"From: {EMAIL_SENDER}")
    print(f"To: {', '.join(RECIPIENT_EMAILS)}")
    print(f"Subject: {subject}")
    
    success, message = send_email(RECIPIENT_EMAILS, subject, html_body)
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS!")
        print("="*60)
        print(f"📧 Email sent to {len(RECIPIENT_EMAILS)} recipient(s):")
        for email in RECIPIENT_EMAILS:
            print(f"   ✓ {email}")
        print("\n🎉 Email automation completed successfully!")
    else:
        print("❌ FAILED!")
        print("="*60)
        print(f"Error: {message}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Check GMAIL_APP_PASSWORD is correct")
        print("   2. Make sure it's a 16-character App Password (not regular password)")
        print("   3. For Gmail: https://myaccount.google.com/apppasswords")
        print("   4. Enable 2-Factor Authentication first")
        sys.exit(1)

if __name__ == "__main__":
    main()
