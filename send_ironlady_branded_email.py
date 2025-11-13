"""
IRON LADY - Email Script for Multiple Team Leader Worksheets
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

# Recipients
CEO_EMAIL = os.getenv('CEO_EMAIL', '').strip()
AUTO_MAIL = os.getenv('AUTO_MAIL', '').strip()

# Clean recipients
recipient_list = []
for email_var in [CEO_EMAIL, AUTO_MAIL]:
    if email_var:
        cleaned = email_var.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        emails = [e.strip() for e in cleaned.replace(',', ' ').split() if e.strip() and '@' in e]
        recipient_list.extend(emails)

RECIPIENT_EMAILS = list(set([e for e in recipient_list if e and '@' in e and '.' in e]))

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

# Team Leader worksheets mapping
TEAM_LEADERS = {
    'Ghazala': 'Ghazala - Rising Stars',
    'Afreen': 'Afreen - High Flyers',
    'Soumya': 'Soumya - Goal Getters',
    'Sweksha': 'Sweksha - Team',
    'NJ - T&E': 'NJ - Training & Excellence'
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
        for idx in range(data_start_idx, len(all_values)):
            row = all_values[idx]
            
            # Stop if we hit another date or empty RM name
            if not row or len(row) < 2:
                break
            
            rm_name = str(row[1]).strip() if len(row) > 1 else ''
            
            if not rm_name or rm_name == '' or 'Nov' in rm_name or 'Jan' in rm_name:
                break
            
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

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(team_summary, team_data):
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
    """Send email"""
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
    print("🚀 Iron Lady Email Automation - Multi-Sheet Version")
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("\n" + "="*60)
    print("CONFIGURATION CHECK")
    print("="*60)
    
    print(f"Gmail: {'✅' if EMAIL_SENDER else '❌'} {EMAIL_SENDER if EMAIL_SENDER else 'Not set'}")
    print(f"Password: {'✅' if EMAIL_PASSWORD else '❌'}")
    print(f"Recipients: {'✅' if RECIPIENT_EMAILS else '❌'} {len(RECIPIENT_EMAILS)} email(s)")
    for email in RECIPIENT_EMAILS:
        print(f"  → {email}")
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
    
    # Create and send email
    if not RECIPIENT_EMAILS:
        print("\n⚠️  No recipients configured - generating email preview only")
        html_body = create_email_html(team_summary, team_data)
        
        with open('email_preview.html', 'w') as f:
            f.write(html_body)
        print("✅ Email preview saved to email_preview.html")
        return
    
    print("\n" + "="*60)
    print("SENDING EMAIL")
    print("="*60)
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(team_summary, team_data)
    
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
