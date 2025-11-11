"""
IRON LADY - Email Script for Google Sheets
Properly reads structured data from Google Sheets
Works with ironlady_sheets_complete.py
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

# User mapping
USERNAME_TO_NAME = {
    'ghazala': 'Ghazala - Rising Stars',
    'megha': 'Megha - Winners',
    'afreen': 'Afreen - High Flyers',
    'soumya': 'Soumya - Goal Getters'
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
        return client
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return None

def get_metrics_data(date_str):
    """Get performance metrics from Metrics sheet"""
    try:
        client = get_sheets_client()
        if not client:
            return pd.DataFrame()
        
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet('Metrics')
        all_data = worksheet.get_all_values()
        
        if len(all_data) <= 1:
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        
        # Filter for date
        df = df[df['Date'] == date_str].copy()
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Convert numeric columns
        numeric_cols = ['WA_Audit_Achieved', 'Call_Audit_Achieved', 'Mocks_Achieved', 
                       'SL_Calls_Achieved', 'Followups_Achieved', 'Pitches_Achieved', 'Current_MC_Achieved']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Aggregate by username
        agg_dict = {
            'RM_Name': 'count',  # Count RMs
            'WA_Audit_Achieved': 'sum',
            'Call_Audit_Achieved': 'sum',
            'Mocks_Achieved': 'sum',
            'SL_Calls_Achieved': 'sum',
            'Followups_Achieved': 'sum',
            'Pitches_Achieved': 'sum',
            'Current_MC_Achieved': 'sum'
        }
        
        grouped = df.groupby('Username').agg(agg_dict).reset_index()
        
        # Rename columns
        grouped.columns = ['Username', 'Total_RMs', 'Total_WA_Audit', 'Total_Call_Audit',
                          'Total_Mocks', 'Total_SL_Calls', 'Total_Registrations', 
                          'Total_Pitches', 'Total_Current_MC']
        
        # Add team leader names
        grouped['Team_Leader'] = grouped['Username'].map(USERNAME_TO_NAME)
        
        # Calculate conversion rate
        grouped['Conversion_Rate'] = grouped.apply(
            lambda row: round((row['Total_Registrations'] / row['Total_Pitches'] * 100), 1)
            if row['Total_Pitches'] > 0 else 0.0,
            axis=1
        )
        
        return grouped
        
    except Exception as e:
        print(f"❌ Error getting metrics: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_checklist_status(date_str):
    """Get checklist status from Checklists sheet"""
    try:
        client = get_sheets_client()
        if not client:
            return {}
        
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet('Checklists')
        all_data = worksheet.get_all_values()
        
        if len(all_data) <= 1:
            return {}
        
        # Create DataFrame
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        
        # Filter for date
        df = df[df['Date'] == date_str].copy()
        
        if len(df) == 0:
            return {}
        
        # Aggregate by username
        checklist_status = {}
        
        for username in df['Username'].unique():
            user_data = df[df['Username'] == username]
            total_tasks = len(user_data)
            completed_tasks = len(user_data[user_data['Completed'].str.upper() == 'TRUE'])
            day_type = user_data['Day_Type'].iloc[0] if len(user_data) > 0 else 'Unknown'
            percentage = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
            
            checklist_status[username] = {
                'day_type': day_type,
                'completed': completed_tasks,
                'total': total_tasks,
                'percentage': percentage
            }
        
        return checklist_status
        
    except Exception as e:
        print(f"⚠️  Could not get checklist status: {e}")
        return {}

def get_upload_status(date_str):
    """Get upload status from Uploads sheet"""
    try:
        client = get_sheets_client()
        if not client:
            return {}
        
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet('Uploads')
        all_data = worksheet.get_all_values()
        
        if len(all_data) <= 1:
            return {}
        
        # Create DataFrame
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        
        # Filter for date
        df = df[df['Date'] == date_str].copy()
        
        if len(df) == 0:
            return {}
        
        # Aggregate by username
        upload_status = {}
        
        for username in df['Username'].unique():
            user_data = df[df['Username'] == username]
            total_files = len(user_data)
            categories = user_data['Category'].unique().tolist()
            latest = user_data['Upload_Time'].max() if len(user_data) > 0 else 'Unknown'
            
            upload_status[username] = {
                'total_files': total_files,
                'categories': categories,
                'latest': latest
            }
        
        return upload_status
        
    except Exception as e:
        print(f"⚠️  Could not get upload status: {e}")
        return {}

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(df, checklist_status={}, upload_status={}):
    """Create HTML email"""
    
    # Calculate totals
    total_rms = int(df['Total_RMs'].sum())
    total_pitches = int(df['Total_Pitches'].sum())
    total_registrations = int(df['Total_Registrations'].sum())
    avg_conversion = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0
    
    total_wa = int(df['Total_WA_Audit'].sum())
    total_call = int(df['Total_Call_Audit'].sum())
    total_mocks = int(df['Total_Mocks'].sum())
    total_sl = int(df['Total_SL_Calls'].sum())
    total_mc = int(df['Total_Current_MC'].sum())
    
    # Team performance table
    table_rows = ""
    for _, row in df.iterrows():
        conv = row['Conversion_Rate']
        if conv >= 15:
            conv_color = IRONLADY_COLORS['success']
            conv_icon = '✅'
        elif conv >= 10:
            conv_color = IRONLADY_COLORS['primary']
            conv_icon = '⚠️'
        else:
            conv_color = '#dc3545'
            conv_icon = '❌'
        
        table_rows += f"""
        <tr>
            <td style="padding: 12px;">{row['Team_Leader']}</td>
            <td style="padding: 12px; text-align: center;">{row['Total_RMs']}</td>
            <td style="padding: 12px; text-align: center;">{row['Total_Pitches']}</td>
            <td style="padding: 12px; text-align: center;">{row['Total_Registrations']}</td>
            <td style="padding: 12px; text-align: center;">
                {conv_icon} <span style="color: {conv_color}; font-weight: 700;">{conv}%</span>
            </td>
        </tr>
        """
    
    # Checklist section
    checklist_html = ""
    if checklist_status:
        checklist_html = f"""
        <h2 class="section-title">✅ Daily Checklist Status</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: {IRONLADY_COLORS['secondary']}; color: white;">
                <th style="padding: 12px; text-align: left;">Team Leader</th>
                <th style="padding: 12px; text-align: center;">Day Type</th>
                <th style="padding: 12px; text-align: center;">Completed</th>
                <th style="padding: 12px; text-align: center;">Progress</th>
                <th style="padding: 12px; text-align: center;">Status</th>
            </tr>
        """
        
        for _, row in df.iterrows():
            username = row['Username']
            team_name = row['Team_Leader']
            
            if username in checklist_status:
                status = checklist_status[username]
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
                    <td style="padding: 12px;">{team_name}</td>
                    <td style="padding: 12px; text-align: center;">{status['day_type']}</td>
                    <td style="padding: 12px; text-align: center;">{status['completed']}/{status['total']}</td>
                    <td style="padding: 12px; text-align: center;">
                        <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div style="background: {status_color}; height: 100%; width: {percentage}%;"></div>
                        </div>
                    </td>
                    <td style="padding: 12px; text-align: center;">
                        {status_icon} <span style="color: {status_color}; font-weight: 700;">{status_text}</span>
                    </td>
                </tr>
                """
            else:
                checklist_html += f"""
                <tr>
                    <td style="padding: 12px;">{team_name}</td>
                    <td style="padding: 12px; text-align: center;" colspan="4">
                        <span style="color: #999;">No data</span>
                    </td>
                </tr>
                """
        
        checklist_html += "</table>"
    else:
        checklist_html = f"""
        <h2 class="section-title">✅ Daily Checklist Status</h2>
        <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; margin: 20px 0;">
            <p>ℹ️ No checklist data available for today.</p>
        </div>
        """
    
    # Upload section
    upload_html = ""
    if upload_status:
        upload_html = f"""
        <h2 class="section-title">📤 Document Upload Status</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: {IRONLADY_COLORS['secondary']}; color: white;">
                <th style="padding: 12px; text-align: left;">Team Leader</th>
                <th style="padding: 12px; text-align: center;">Total Files</th>
                <th style="padding: 12px; text-align: left;">Categories</th>
                <th style="padding: 12px; text-align: center;">Status</th>
            </tr>
        """
        
        for _, row in df.iterrows():
            username = row['Username']
            team_name = row['Team_Leader']
            
            if username in upload_status:
                status = upload_status[username]
                total_files = status['total_files']
                categories = ', '.join(status['categories'][:3])
                if len(status['categories']) > 3:
                    categories += f" (+{len(status['categories']) - 3} more)"
                
                status_icon = '✅' if total_files > 0 else '❌'
                status_text = f'{total_files} uploaded' if total_files > 0 else 'No uploads'
                status_color = IRONLADY_COLORS['success'] if total_files > 0 else '#dc3545'
                
                upload_html += f"""
                <tr>
                    <td style="padding: 12px;">{team_name}</td>
                    <td style="padding: 12px; text-align: center; font-weight: 700;">{total_files}</td>
                    <td style="padding: 12px;"><small>{categories}</small></td>
                    <td style="padding: 12px; text-align: center;">
                        {status_icon} <span style="color: {status_color}; font-weight: 700;">{status_text}</span>
                    </td>
                </tr>
                """
            else:
                upload_html += f"""
                <tr>
                    <td style="padding: 12px;">{team_name}</td>
                    <td style="padding: 12px; text-align: center;" colspan="3">
                        <span style="color: #999;">No uploads</span>
                    </td>
                </tr>
                """
        
        upload_html += "</table>"
    else:
        upload_html = f"""
        <h2 class="section-title">📤 Document Upload Status</h2>
        <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; margin: 20px 0;">
            <p>ℹ️ No upload data available for today.</p>
        </div>
        """
    
    # Complete HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: {IRONLADY_COLORS['accent']}; margin: 0; padding: 0; }}
            .container {{ max-width: 900px; margin: 20px auto; background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
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
                    <strong>WA Audit:</strong> {total_wa}<br/>
                    <strong>Call Audit:</strong> {total_call}<br/>
                    <strong>Mocks:</strong> {total_mocks}<br/>
                    <strong>SL Calls:</strong> {total_sl}<br/>
                    <strong>Current MC Registrations:</strong> {total_mc}
                </div>
                
                <h2 class="section-title">🏆 Team Leader Performance</h2>
                <table>
                    <tr>
                        <th>Team Leader</th>
                        <th style="text-align: center;">RMs</th>
                        <th style="text-align: center;">Pitches</th>
                        <th style="text-align: center;">Registrations</th>
                        <th style="text-align: center;">Conversion %</th>
                    </tr>
                    {table_rows}
                </table>
                
                {checklist_html}
                
                {upload_html}
                
                <h2 class="section-title">💡 Key Insights</h2>
                <div class="metric">
                    {'✅ <strong>Excellent!</strong> Team meeting targets.' if avg_conversion >= 15 else '⚠️ <strong>Action needed:</strong> Below 15% target.'}
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
    print("🚀 Iron Lady Email Automation")
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
    
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, RECIPIENT_EMAILS, SHEET_ID, CREDENTIALS_JSON]):
        print("\n❌ Missing required configuration!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("FETCHING DATA FROM GOOGLE SHEETS")
    print("="*60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get performance data
    df = get_metrics_data(today)
    
    if len(df) == 0:
        print(f"\n❌ No performance data for {today}")
        sys.exit(1)
    
    print(f"✅ Performance data: {len(df)} team leaders")
    for _, row in df.iterrows():
        print(f"  → {row['Team_Leader']}: {row['Total_Pitches']} pitches, {row['Total_Registrations']} regs ({row['Conversion_Rate']}%)")
    
    # Get checklist data
    print("\n" + "="*60)
    print("FETCHING CHECKLIST STATUS")
    print("="*60)
    
    checklist_status = get_checklist_status(today)
    if checklist_status:
        print(f"✅ Checklist data: {len(checklist_status)} team leaders")
        for username, status in checklist_status.items():
            print(f"  → {username}: {status['completed']}/{status['total']} ({status['percentage']}%) - {status['day_type']}")
    else:
        print("ℹ️  No checklist data")
    
    # Get upload data
    print("\n" + "="*60)
    print("FETCHING UPLOAD STATUS")
    print("="*60)
    
    upload_status = get_upload_status(today)
    if upload_status:
        print(f"✅ Upload data: {len(upload_status)} team leaders")
        for username, status in upload_status.items():
            print(f"  → {username}: {status['total_files']} files")
    else:
        print("ℹ️  No upload data")
    
    # Create and send email
    print("\n" + "="*60)
    print("SENDING EMAIL")
    print("="*60)
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(df, checklist_status, upload_status)
    
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
