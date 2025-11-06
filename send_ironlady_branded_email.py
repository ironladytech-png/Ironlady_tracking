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
# DOCUMENT UPLOAD RESULTS
# ============================================

def create_document_upload_html(upload_data):
    """Create HTML section for uploaded documents with OCR/NER results"""
    if not upload_data:
        return ""
    
    html = f"""
                <h2 class="section-title">📁 Document Upload Summary</h2>
                <div style="background: white; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
    """
    
    total_files = 0
    ocr_files = 0
    ner_files = 0
    
    for category, files in upload_data.items():
        if files:
            total_files += len(files)
            html += f"""
                    <h3 style="color: {IRONLADY_COLORS['secondary']}; margin: 15px 0 10px 0; border-bottom: 2px solid {IRONLADY_COLORS['accent']}; padding-bottom: 5px;">
                        {category}
                    </h3>
                    <ul style="margin: 5px 0; padding-left: 20px;">
            """
            
            for file in files:
                html += f"""
                        <li style="margin: 8px 0;">
                            <strong>{file['name']}</strong> ({file['size']/1024:.1f} KB)
                            <br/>
                            <small style="color: #666;">Uploaded: {file['upload_time']}</small>
                """
                
                # Add OCR results if available
                if file.get('has_ocr'):
                    ocr_files += 1
                    text_preview = file.get('ocr_text', '')[:200] + '...' if len(file.get('ocr_text', '')) > 200 else file.get('ocr_text', '')
                    html += f"""
                            <br/>
                            <span style="background: #d4edda; padding: 2px 8px; border-radius: 3px; font-size: 0.85rem;">
                                ✅ OCR Processed
                            </span>
                            <br/>
                            <small style="color: #555; font-style: italic;">Text: {text_preview}</small>
                    """
                
                # Add NER results if available
                if file.get('has_ner') and file.get('entities'):
                    ner_files += 1
                    entities = file['entities']
                    entity_summary = []
                    
                    if entities.get('PERSON'):
                        entity_summary.append(f"👤 {len(entities['PERSON'])} people")
                    if entities.get('DATE'):
                        entity_summary.append(f"📅 {len(entities['DATE'])} dates")
                    if entities.get('PHONE'):
                        entity_summary.append(f"📞 {len(entities['PHONE'])} phones")
                    if entities.get('EMAIL'):
                        entity_summary.append(f"📧 {len(entities['EMAIL'])} emails")
                    
                    if entity_summary:
                        html += f"""
                            <br/>
                            <span style="background: #cfe2ff; padding: 2px 8px; border-radius: 3px; font-size: 0.85rem;">
                                🧠 NER: {', '.join(entity_summary)}
                            </span>
                        """
                
                # Add metrics if available
                if file.get('metrics'):
                    metrics = file['metrics']
                    metric_summary = []
                    
                    if metrics.get('pitches'):
                        metric_summary.append(f"Pitches: {metrics['pitches'][0]}")
                    if metrics.get('registrations'):
                        metric_summary.append(f"Regs: {metrics['registrations'][0]}")
                    if metrics.get('leads'):
                        metric_summary.append(f"Leads: {metrics['leads'][0]}")
                    
                    if metric_summary:
                        html += f"""
                            <br/>
                            <span style="background: #fff3cd; padding: 2px 8px; border-radius: 3px; font-size: 0.85rem;">
                                📊 Metrics: {', '.join(metric_summary)}
                            </span>
                        """
                
                html += """
                        </li>
                """
            
            html += """
                    </ul>
            """
    
    # Add summary
    html += f"""
                    <div style="margin-top: 20px; padding: 15px; background: {IRONLADY_COLORS['accent']}; border-radius: 5px;">
                        <strong>Summary:</strong><br/>
                        📄 Total Files: {total_files} | 
                        ✅ OCR Processed: {ocr_files} | 
                        🧠 NER Analyzed: {ner_files}
                    </div>
                </div>
    """
    
    return html

# ============================================
# CHECKLIST DATA
# ============================================

DAILY_CHECKLISTS = {
    'Day 1-1': [
        'Mocks - Who are the people - Buddy structure',
        'Sign off Activities - each RM type',
        'WA Audit - Minimum 10',
        'Follow up Calls - 2 Registrations',
        'SL Calls - 5 (Share status list)',
        'Lead Analysis AI summary',
        'Call Audit - Minimum 5 calls',
        'Tracking: CRM Update, Call/Attendance/WA',
        'Targets Sharing - percentage and potential list',
        'CRM Updation',
        'Sharing hot prospects list',
    ],
    'Day 1': [
        'WA Audit - 10',
        'SL Calls - 8 (Share status list)',
        'Sign off Activities',
        'Mocks - Buddy structure',
        '30s pitch Prep',
        'Tracking: CRM Update',
        'Call Audit - Minimum 5 calls',
        'Targets Sharing - % and potential list',
        '10% Conversion - action points',
        'CRM Updation - including attendance',
        'Sharing hot prospects list and Tracking',
    ],
    'Day 2': [
        'SL Calls - 10-12 (Share status list)',
        'WA Audit - As needed',
        'Tracking: CRM Update',
        'Sign off Activities',
        'Targets Sharing - 10% before, 15% after',
        'CRM Updation - including attendance',
        'Sharing hot prospects list and Tracking',
    ]
}

def get_checklist_data():
    """
    Get checklist completion data from Google Sheets (optional)
    Returns dictionary with day type and completion status
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
        
        if not credentials_json or not sheet_id:
            return None
        
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
        
        # Try to find a "Checklist" worksheet
        try:
            worksheet = spreadsheet.worksheet("Checklist")
            data = worksheet.get_all_records()
            if data:
                return pd.DataFrame(data)
        except:
            pass
        
        return None
    
    except Exception as e:
        print(f"⚠️ Could not fetch checklist data: {e}")
        return None

def get_upload_data():
    """
    Get document upload data with OCR/NER results from Google Sheets (optional)
    Expected worksheet name: "Uploads"
    Expected columns: category, name, size, upload_time, ocr_text, entities, metrics
    Returns dict organized by category
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "").strip()
        sheet_id = os.getenv('GOOGLE_SHEET_ID', '').strip()
        
        if not credentials_json or not sheet_id:
            return None
        
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
            if data:
                df = pd.DataFrame(data)
                
                # Organize by category
                upload_dict = {}
                for category in df['category'].unique():
                    category_data = df[df['category'] == category].to_dict('records')
                    
                    # Parse JSON fields if they exist
                    for item in category_data:
                        if 'entities' in item and item['entities']:
                            try:
                                item['entities'] = json.loads(item['entities'])
                                item['has_ner'] = True
                            except:
                                pass
                        if 'metrics' in item and item['metrics']:
                            try:
                                item['metrics'] = json.loads(item['metrics'])
                            except:
                                pass
                        if 'ocr_text' in item and item['ocr_text']:
                            item['has_ocr'] = True
                    
                    upload_dict[category] = category_data
                
                return upload_dict
        except Exception as e:
            print(f"⚠️ No 'Uploads' worksheet found: {e}")
            pass
        
        return None
    
    except Exception as e:
        print(f"⚠️ Could not fetch upload data: {e}")
        return None

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================

def get_data_from_sheets():
    """
    Fetch data from Google Sheets using GOOGLE_SHEETS_CREDENTIALS
    Returns None if not configured - NO DUMMY DATA
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Get credentials from environment (your GOOGLE_SHEETS_CREDENTIALS secret)
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
        worksheet = spreadsheet.sheet1
        data = worksheet.get_all_records()
        
        if not data:
            print("⚠️ Google Sheet is empty")
            return None
        
        print(f"✅ Loaded {len(data)} rows from Google Sheets")
        df = pd.DataFrame(data)
        
        # Ensure required columns exist
        required_cols = ['Team_Leader', 'Total_RMs', 'Total_Pitches', 'Total_Registrations']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"⚠️ Missing columns in sheet: {missing_cols}")
            print(f"📋 Available columns: {list(df.columns)}")
            return None
        
        # Calculate conversion rate if not present
        if 'Conversion_Rate' not in df.columns:
            df['Conversion_Rate'] = df.apply(
                lambda row: round((row['Total_Registrations'] / row['Total_Pitches'] * 100), 1) 
                if row['Total_Pitches'] > 0 else 0,
                axis=1
            )
        
        return df
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid GOOGLE_SHEETS_CREDENTIALS JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        return None

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(df, checklist_data=None, day_type='Day 1-1', upload_data=None):
    """Create HTML email with Iron Lady branding including checklist and uploads"""
    
    # Calculate totals
    total_rms = int(df['Total_RMs'].sum())
    total_pitches = int(df['Total_Pitches'].sum())
    total_registrations = int(df['Total_Registrations'].sum())
    avg_conversion = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0
    
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
    
    # Create checklist section
    checklist_html = ""
    if day_type in DAILY_CHECKLISTS:
        tasks = DAILY_CHECKLISTS[day_type]
        checklist_html = f"""
                <h2 class="section-title">✅ Daily Checklist - {day_type}</h2>
                <div style="background: white; padding: 20px; border-left: 5px solid {IRONLADY_COLORS['primary']}; margin: 20px 0;">
                    <p style="margin: 0 0 15px 0; font-weight: 700;">Tasks for {day_type}:</p>
                    <ul style="margin: 0; padding-left: 20px;">
        """
        for task in tasks:
            checklist_html += f"""
                        <li style="margin: 8px 0; padding: 5px 0;">{task}</li>
        """
        checklist_html += """
                    </ul>
                    <p style="margin: 15px 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                        ℹ️ Use the Streamlit dashboard to track completion status
                    </p>
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
                
                {checklist_html}
                
                {create_document_upload_html(upload_data) if upload_data else ''}
                
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
    print("📊 FETCHING DATA FROM GOOGLE SHEETS")
    print("="*60)
    
    df = get_data_from_sheets()
    
    if df is None or len(df) == 0:
        print("\n❌ NO DATA AVAILABLE!")
        print("\n💡 SOLUTIONS:")
        print("   1. Make sure GOOGLE_SHEETS_CREDENTIALS is set (full JSON)")
        print("   2. Make sure GOOGLE_SHEET_ID is set")
        print("   3. Verify your Google Sheet has data")
        print("   4. Required columns: Team_Leader, Total_RMs, Total_Pitches, Total_Registrations")
        print("   5. Share your sheet with the service account email")
        print("\n📖 See GITHUB_ACTIONS_SETUP.md for detailed instructions")
        sys.exit(1)
    
    print(f"✅ Data ready: {len(df)} team leaders")
    print(f"📋 Team Leaders: {', '.join(df['Team_Leader'].tolist())}")
    
    # Create email
    print("\n" + "="*60)
    print("📝 CREATING EMAIL")
    print("="*60)
    
    # Determine day type (you can add this as an environment variable if needed)
    day_type = os.getenv('DAY_TYPE', 'Day 1-1')
    print(f"📅 Day Type: {day_type}")
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')} - {day_type}"
    
    # Try to get checklist data
    checklist_df = get_checklist_data()
    if checklist_df is not None:
        print(f"✅ Checklist data loaded")
    else:
        print(f"ℹ️  Using default checklist items (no completion data)")
    
    # Try to get upload data (documents with OCR/NER results)
    upload_data = get_upload_data()
    if upload_data:
        print(f"✅ Document upload data loaded")
        total_uploads = sum(len(files) for files in upload_data.values())
        print(f"📁 Total uploaded documents: {total_uploads}")
    else:
        print(f"ℹ️  No document uploads found")
    
    html_body = create_email_html(df, checklist_df, day_type, upload_data)
    print("✅ Email HTML created with all sections")
    
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
