"""
IRON LADY - Email Automation Script for GitHub Actions
Sends daily branded email reports without Streamlit dependency
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# ============================================
# CONFIGURATION
# ============================================

# Email configuration from environment variables (GitHub Secrets)
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))

# Recipients
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '').split(',')

# Iron Lady Colors
IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
}

# ============================================
# GOOGLE SHEETS CONNECTION (Optional)
# ============================================

def get_data_from_sheets():
    """
    Fetch data from Google Sheets
    Returns sample data if Google Sheets not configured
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Get credentials from environment
        credentials_dict = {
            "type": os.getenv("GCP_TYPE"),
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GCP_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.getenv("GCP_CLIENT_EMAIL"),
            "client_id": os.getenv("GCP_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL")
        }
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
        )
        
        client = gspread.authorize(credentials)
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        if sheet_id:
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
    
    except Exception as e:
        print(f"⚠️ Could not fetch from Google Sheets: {e}")
    
    # Return sample data
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
    
    # Check configuration
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("❌ ERROR: Email credentials not configured")
        print("Please set EMAIL_SENDER and EMAIL_PASSWORD in GitHub Secrets")
        sys.exit(1)
    
    if not RECIPIENT_EMAILS or RECIPIENT_EMAILS == ['']:
        print("❌ ERROR: No recipient emails configured")
        print("Please set RECIPIENT_EMAILS in GitHub Secrets")
        sys.exit(1)
    
    print(f"📧 Email Sender: {EMAIL_SENDER}")
    print(f"📬 Recipients: {', '.join(RECIPIENT_EMAILS)}")
    
    # Get data
    print("\n📊 Fetching data...")
    df = get_data_from_sheets()
    print(f"✅ Data loaded: {len(df)} team leaders")
    
    # Create email
    print("\n📝 Creating email...")
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(df)
    print("✅ Email HTML created")
    
    # Send email
    print("\n📤 Sending email...")
    success, message = send_email(RECIPIENT_EMAILS, subject, html_body)
    
    if success:
        print(f"✅ {message}")
        print(f"📧 Sent to: {', '.join(RECIPIENT_EMAILS)}")
    else:
        print(f"❌ {message}")
        sys.exit(1)
    
    print("\n🎉 Email automation completed successfully!")

if __name__ == "__main__":
    main()
