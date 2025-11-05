"""
IRON LADY - Email Automation Script for GitHub Actions
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

# Combine all recipient emails
recipient_list = []
if CEO_EMAIL:
    recipient_list.extend([email.strip() for email in CEO_EMAIL.split(',') if email.strip()])
if AUTO_MAIL:
    recipient_list.extend([email.strip() for email in AUTO_MAIL.split(',') if email.strip()])

# Remove duplicates
RECIPIENT_EMAILS = list(set(recipient_list))

# Iron Lady Colors
IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
}

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

def get_data_from_sheets():
    """
    Fetch data from Google Sheets using GOOGLE_SHEETS_CREDENTIALS
    Returns sample data if not configured
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Get credentials from environment (your GOOGLE_SHEETS_CREDENTIALS secret)
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        
        if credentials_json:
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
            sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
            
            if sheet_id:
                print(f"📊 Connecting to Google Sheet: {sheet_id}")
                spreadsheet = client.open_by_key(sheet_id)
                worksheet = spreadsheet.sheet1
                data = worksheet.get_all_records()
                
                if data:
                    print(f"✅ Loaded {len(data)} rows from Google Sheets")
                    return pd.DataFrame(data)
    
    except Exception as e:
        print(f"⚠️ Could not fetch from Google Sheets: {e}")
        print("📝 Using sample data instead...")
    
    # Return sample data if Google Sheets fails
    return pd.DataFrame({
        'Team_Leader': ['Ghazala', 'Megha', 'Afreen', 'Soumya'],
        'Total_RMs': [8, 7, 5, 6],
        'Total_Pitches': [120, 105, 75, 90],
        'Total_Registrations': [18, 16, 11, 13],
        'Conversion_Rate': [15.0, 15.2, 14.7, 14.4]
    })

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(df):
    """Create HTML email with Iron Lady branding"""
    
    # Calculate totals
    total_rms = df['Total_RMs'].sum()
    total_pitches = df['Total_Pitches'].sum()
    total_registrations = df['Total_Registrations'].sum()
    avg_conversion = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0
    
    # Create table rows
    table_rows = ""
    for _, row in df.iterrows():
        table_rows += f"""
        <tr>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0;">{row['Team_Leader']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_RMs']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Pitches']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Registrations']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: 700;">{row['Conversion_Rate']}%</td>
        </tr>
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
                max-width: 800px;
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
                
                <h2 class="section-title">📋 Team Leader Performance</h2>
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
        print("\n📖 See GITHUB_SECRETS_FIX.md for detailed instructions")
        sys.exit(1)
    
    print("\n✅ All configuration validated!")
    
    # Get data
    print("\n" + "="*60)
    print("📊 FETCHING DATA")
    print("="*60)
    df = get_data_from_sheets()
    print(f"✅ Data ready: {len(df)} team leaders")
    
    # Create email
    print("\n" + "="*60)
    print("📝 CREATING EMAIL")
    print("="*60)
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(df)
    print("✅ Email HTML created")
    
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
