"""
IRON LADY - GOOGLE SHEETS INTEGRATED EMAIL REPORT
Pulls data from Google Sheets and sends branded email
"""

import smtplib
import os
import sys
from datetime import datetime
import json

# Try to import Google Sheets libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("⚠️ Google Sheets libraries not available")

# ============================================
# OFFICIAL IRON LADY COMPANY COLORS
# ============================================

IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
    'warning': '#F77F00',
    'danger': '#D62828',
    'light': '#FAF3E0',
    'dark': '#1A1A1A',
}

# ============================================
# TEAM LEADERS
# ============================================

TEAM_LEADERS = [
    'Ghazala',
    'Megha',
    'Afreen',  # TL trainee
    'Soumya'   # TL trainee
]

# ============================================
# GOOGLE SHEETS INTEGRATION
# ============================================

def connect_to_google_sheets():
    """Connect to Google Sheets using service account credentials"""
    try:
        # Get credentials from environment variable (GitHub Secret)
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        
        if not creds_json:
            print("❌ GOOGLE_SHEETS_CREDENTIALS not found")
            return None
        
        # Parse JSON credentials
        creds_dict = json.loads(creds_json)
        
        # Create credentials
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        # Authorize and return client
        client = gspread.authorize(credentials)
        print("✅ Connected to Google Sheets")
        return client
        
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None

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
            print(f"📊 Reading sheet: {sheet_name}")
            
            # Get all values
            records = worksheet.get_all_records()
            
            if records:
                data[sheet_name] = records
        
        return data
        
    except Exception as e:
        print(f"❌ Error fetching sheet data: {e}")
        return None

def parse_rm_data(sheet_data):
    """Parse RM data from Google Sheets"""
    try:
        rm_data = []
        
        # Look for sheets with RM data
        for sheet_name, records in sheet_data.items():
            sheet_lower = sheet_name.lower()
            
            # Parse WA Audits, Call Audits, etc.
            if any(keyword in sheet_lower for keyword in ['wa', 'call', 'audit', 'mock']):
                for row in records:
                    rm_name = row.get('RM Name', '').strip()
                    
                    if rm_name and not rm_name.startswith('#'):
                        # Extract data
                        entry = {
                            'name': rm_name,
                            'rms': int(row.get('Total RMs', 0) or 0),
                            'pitches_target': int(row.get('Target Pitch', 0) or row.get('Target', 0) or 0),
                            'pitches_actual': int(row.get('Actual Pitch', 0) or row.get('Achieved', 0) or 0),
                            'reg_target': int(row.get('Target Registration', 0) or row.get('Target Reg', 0) or 0),
                            'reg_actual': int(row.get('Actual Registration', 0) or row.get('Actual Reg', 0) or 0),
                        }
                        
                        # Calculate conversion
                        if entry['pitches_actual'] > 0:
                            entry['conversion'] = round((entry['reg_actual'] / entry['pitches_actual']) * 100, 1)
                        else:
                            entry['conversion'] = 0
                        
                        rm_data.append(entry)
        
        return rm_data
        
    except Exception as e:
        print(f"❌ Error parsing RM data: {e}")
        return []

def calculate_totals(rm_data):
    """Calculate total metrics from RM data"""
    if not rm_data:
        return None
    
    total_rms = sum(rm.get('rms', 0) for rm in rm_data)
    total_pitch_target = sum(rm.get('pitches_target', 0) for rm in rm_data)
    total_pitch_actual = sum(rm.get('pitches_actual', 0) for rm in rm_data)
    total_reg_target = sum(rm.get('reg_target', 0) for rm in rm_data)
    total_reg_actual = sum(rm.get('reg_actual', 0) for rm in rm_data)
    
    pitch_achievement = round((total_pitch_actual / total_pitch_target * 100), 1) if total_pitch_target > 0 else 0
    reg_achievement = round((total_reg_actual / total_reg_target * 100), 1) if total_reg_target > 0 else 0
    conversion_rate = round((total_reg_actual / total_pitch_actual * 100), 1) if total_pitch_actual > 0 else 0
    
    return {
        'total_leads': total_rms * 10,  # Approximate
        'pitch_target': total_pitch_target,
        'pitch_actual': total_pitch_actual,
        'pitch_achievement': pitch_achievement,
        'reg_target': total_reg_target,
        'reg_actual': total_reg_actual,
        'reg_achievement': reg_achievement,
        'conversion_rate': conversion_rate,
        'team_leads': rm_data
    }

# ============================================
# EMAIL GENERATION
# ============================================

def get_performance_status(percentage):
    if percentage >= 90:
        return "Excellent", IRONLADY_COLORS['success'], "🎯"
    elif percentage >= 75:
        return "Good", IRONLADY_COLORS['warning'], "✅"
    elif percentage >= 60:
        return "Fair", IRONLADY_COLORS['warning'], "⚠️"
    else:
        return "Needs Attention", IRONLADY_COLORS['danger'], "❌"

def generate_team_lead_table(team_data):
    if not team_data:
        return ""
    
    html = f"""
    <table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: white;">
        <thead>
            <tr style="background: {IRONLADY_COLORS['dark']};">
                <th style="padding: 18px; text-align: left; color: white; font-weight: 900;">Team Leader</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900;">RMs</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900;">Pitches</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900;">Registrations</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900;">Conversion</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900;">Status</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, lead in enumerate(team_data):
        bg_color = IRONLADY_COLORS['light'] if idx % 2 == 0 else 'white'
        conversion = float(lead.get('conversion', 0))
        status_text, status_color, status_icon = get_performance_status(conversion)
        
        html += f"""
        <tr style="background: {bg_color};">
            <td style="padding: 18px; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">{lead.get('name', 'Unknown')}</td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']};">{lead.get('rms', 0)}</td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']};">
                <span style="font-weight: 900;">{lead.get('pitches_actual', 0)}</span>/{lead.get('pitches_target', 0)}
            </td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']};">
                <span style="font-weight: 900;">{lead.get('reg_actual', 0)}</span>/{lead.get('reg_target', 0)}
            </td>
            <td style="padding: 18px; text-align: center; color: {status_color}; font-weight: 900;">
                {conversion:.1f}%
            </td>
            <td style="padding: 18px; text-align: center;">
                <span style="background: {status_color}; color: white; padding: 8px 16px; font-weight: 700;">
                    {status_icon} {status_text}
                </span>
            </td>
        </tr>
        """
    
    html += "</tbody></table>"
    return html

def generate_email_html(report_data):
    today = datetime.now()
    formatted_date = today.strftime('%A, %B %d, %Y')
    formatted_time = today.strftime('%I:%M %p IST')
    
    if not report_data:
        report_data = {
            'total_leads': 0,
            'pitch_target': 0,
            'pitch_actual': 0,
            'pitch_achievement': 0,
            'reg_target': 0,
            'reg_actual': 0,
            'reg_achievement': 0,
            'conversion_rate': 0,
            'team_leads': []
        }
    
    overall_status, overall_color, overall_icon = get_performance_status(report_data['conversion_rate'])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Iron Lady Daily Report</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background: {IRONLADY_COLORS['light']};">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 40px; text-align: center; margin-bottom: 30px; border-top: 8px solid {IRONLADY_COLORS['primary']}; border-bottom: 8px solid {IRONLADY_COLORS['primary']};">
                <h1 style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 3rem; font-weight: 900; letter-spacing: 3px;">IRON LADY</h1>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 15px 0 0 0;">Sales Performance Management System</p>
                <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 120px; margin: 25px auto;"></div>
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 20px 0 5px 0; font-size: 1.5rem;">DAILY PERFORMANCE REPORT</h2>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0;">{formatted_date}</p>
            </div>
            
            <div style="background: white; padding: 30px; margin-bottom: 25px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 25px 0; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px;">EXECUTIVE SUMMARY</h2>
                
                <table style="width: 100%; margin-bottom: 25px;">
                    <tr>
                        <td style="width: 50%; padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                            <p style="margin: 0; font-weight: 600;">Total Leads</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['primary']}; font-size: 2.5rem; font-weight: 900;">{report_data['total_leads']}</p>
                        </td>
                        <td style="width: 50%; padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['success']};">
                            <p style="margin: 0; font-weight: 600;">Pitch Achievement</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['success']}; font-size: 2.5rem; font-weight: 900;">{report_data['pitch_achievement']:.0f}%</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['warning']};">
                            <p style="margin: 0; font-weight: 600;">Registration Achievement</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['warning']}; font-size: 2.5rem; font-weight: 900;">{report_data['reg_achievement']:.0f}%</p>
                        </td>
                        <td style="padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {overall_color};">
                            <p style="margin: 0; font-weight: 600;">Conversion Rate</p>
                            <p style="margin: 10px 0 0 0; color: {overall_color}; font-size: 2.5rem; font-weight: 900;">{report_data['conversion_rate']:.1f}%</p>
                        </td>
                    </tr>
                </table>
                
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-left: 6px solid {overall_color};">
                    <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700; font-size: 1.1rem;">
                        {overall_icon} Overall Status: {overall_status}
                    </p>
                </div>
            </div>
            
            <div style="background: white; padding: 30px; margin-bottom: 25px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px;">TEAM LEADER PERFORMANCE</h2>
                {generate_team_lead_table(report_data.get('team_leads', []))}
            </div>
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 25px; text-align: center; border-top: 5px solid {IRONLADY_COLORS['primary']}; border-bottom: 5px solid {IRONLADY_COLORS['primary']};">
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-weight: 900; font-size: 1.3rem;">IRON LADY</p>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 10px 0 0 0;">Generated at {formatted_time}</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html

# ============================================
# EMAIL SENDING
# ============================================

def send_daily_email():
    print("🔍 Checking environment variables...")
    sender_email = os.getenv('GMAIL_USER')
    sender_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient_email = os.getenv('CEO_EMAIL')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    print(f"GMAIL_USER: {bool(sender_email)}")
    print(f"GMAIL_APP_PASSWORD: {bool(sender_password)}")
    print(f"CEO_EMAIL: {bool(recipient_email)}")
    print(f"GOOGLE_SHEET_ID: {bool(sheet_id)}")
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ Missing email configuration")
        return False
    
    # Fetch data from Google Sheets
    report_data = None
    if sheet_id and GSHEETS_AVAILABLE:
        print(f"📊 Fetching data from Google Sheets: {sheet_id}")
        sheet_data = fetch_sheet_data(sheet_id)
        
        if sheet_data:
            rm_data = parse_rm_data(sheet_data)
            report_data = calculate_totals(rm_data)
            print(f"✅ Loaded data for {len(rm_data)} team leaders")
        else:
            print("⚠️ No data from Google Sheets, using defaults")
    else:
        print("⚠️ Google Sheets not configured, using default data")
    
    try:
        print("📧 Generating email HTML...")
        html_content = generate_email_html(report_data)
        
        print("🔌 Connecting to Gmail...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            print("🔐 Logging in...")
            server.login(sender_email, sender_password)
            
            print("📤 Sending email...")
            msg = f"From: {sender_email}\r\n"
            msg += f"To: {recipient_email}\r\n"
            msg += f"Subject: Iron Lady Daily Report | {datetime.now().strftime('%B %d, %Y')}\r\n"
            msg += "Content-Type: text/html; charset=utf-8\r\n"
            msg += "\r\n"
            msg += html_content
            
            server.sendmail(sender_email, recipient_email, msg.encode('utf-8'))
        
        print(f"✅ Email sent to {recipient_email}")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IRON LADY - Daily Email Report (Google Sheets)")
    print("=" * 60)
    print(f"🕐 {datetime.now().strftime('%I:%M %p IST on %B %d, %Y')}")
    print()
    
    print("Team Leaders: Ghazala, Megha, Afreen (trainee), Soumya (trainee)")
    print()
    
    success = send_daily_email()
    
    print()
    if success:
        print("🎉 Email sent successfully!")
    else:
        print("❌ Failed to send email")
    print("=" * 60)
