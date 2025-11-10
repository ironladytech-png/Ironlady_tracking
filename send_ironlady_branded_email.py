"""
IRON LADY - Email Automation Script (SQLite Version)
Reads data from ironlady.db (same database as Streamlit app)
Sends daily performance reports with checklist and upload status
"""

import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import sys

# ============================================
# CONFIGURATION
# ============================================

# Email configuration
EMAIL_SENDER = os.getenv('GMAIL_USER', '').strip()
EMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '').strip()
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# Recipients
CEO_EMAIL = os.getenv('CEO_EMAIL', '').strip()
AUTO_MAIL = os.getenv('AUTO_MAIL', '').strip()

# Clean and combine recipient emails
recipient_list = []

if CEO_EMAIL:
    cleaned = CEO_EMAIL.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    emails = [email.strip() for email in cleaned.replace(',', ' ').split() if email.strip() and '@' in email]
    recipient_list.extend(emails)

if AUTO_MAIL:
    cleaned = AUTO_MAIL.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    emails = [email.strip() for email in cleaned.replace(',', ' ').split() if email.strip() and '@' in email]
    recipient_list.extend(emails)

RECIPIENT_EMAILS = list(set([email for email in recipient_list if email and '@' in email and '.' in email]))

# Iron Lady Colors
IRONLADY_COLORS = {
    'primary': '#E63946',
    'secondary': '#1A1A1A',
    'accent': '#F5E6D3',
    'success': '#2A9D8F',
}

# Database file
DB_FILE = 'ironlady.db'

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_team_performance_data(date_str=None):
    """
    Get team performance data from SQLite database
    If date_str is None, gets data from today
    """
    try:
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DB_FILE, timeout=10)
        
        # Query to get aggregated data per team leader
        query = '''
            SELECT 
                u.username,
                u.name as Team_Leader,
                u.team_size as Total_RMs,
                COALESCE(SUM(m.wa_audit_achieved), 0) as Total_WA_Audit,
                COALESCE(SUM(m.call_audit_achieved), 0) as Total_Call_Audit,
                COALESCE(SUM(m.mocks_achieved), 0) as Total_Mocks,
                COALESCE(SUM(m.sl_calls_achieved), 0) as Total_SL_Calls,
                COALESCE(SUM(m.pitches_achieved), 0) as Total_Pitches,
                COALESCE(SUM(m.followups_achieved), 0) as Total_Registrations,
                COALESCE(SUM(m.current_mc_achieved), 0) as Total_Current_MC
            FROM users u
            LEFT JOIN rm_daily_metrics m ON u.username = m.username AND m.date = ?
            GROUP BY u.username, u.name, u.team_size
            ORDER BY u.name
        '''
        
        df = pd.read_sql_query(query, conn, params=(date_str,))
        conn.close()
        
        if len(df) > 0:
            # Calculate conversion rate
            df['Conversion_Rate'] = df.apply(
                lambda row: round((row['Total_Registrations'] / row['Total_Pitches'] * 100), 1) 
                if row['Total_Pitches'] > 0 else 0.0,
                axis=1
            )
        
        return df
    
    except Exception as e:
        print(f"❌ Error fetching team performance: {e}")
        return pd.DataFrame()

def get_checklist_status(date_str=None):
    """
    Get checklist completion status for each team leader
    Returns dict: {username: {'day_type': 'Day 1-1', 'completed': 15, 'total': 20, 'percentage': 75}}
    """
    try:
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DB_FILE, timeout=10)
        cursor = conn.cursor()
        
        # Get checklist data for each user
        cursor.execute('''
            SELECT username, day_type, COUNT(*) as total_tasks, 
                   SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_tasks
            FROM checklists
            WHERE date = ?
            GROUP BY username, day_type
        ''', (date_str,))
        
        results = cursor.fetchall()
        conn.close()
        
        checklist_status = {}
        for row in results:
            username, day_type, total_tasks, completed_tasks = row
            percentage = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
            
            checklist_status[username] = {
                'day_type': day_type,
                'completed': completed_tasks,
                'total': total_tasks,
                'percentage': percentage
            }
        
        return checklist_status
    
    except Exception as e:
        print(f"⚠️ Could not fetch checklist data: {e}")
        return {}

def get_upload_status(date_str=None):
    """
    Get document upload status for each team leader
    Returns dict: {username: {'total_files': 5, 'categories': ['WA Audit', 'Call Recording'], 'latest': '2024-11-07'}}
    """
    try:
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DB_FILE, timeout=10)
        
        # Get upload data for each user
        query = '''
            SELECT username, category, filename, upload_time
            FROM uploads
            WHERE date = ?
            ORDER BY upload_time DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(date_str,))
        conn.close()
        
        if len(df) == 0:
            return {}
        
        # Aggregate by username
        upload_status = {}
        
        for username in df['username'].unique():
            user_data = df[df['username'] == username]
            total_files = len(user_data)
            categories = user_data['category'].unique().tolist()
            latest = user_data['upload_time'].iloc[0] if len(user_data) > 0 else 'Unknown'
            
            upload_status[username] = {
                'total_files': total_files,
                'categories': categories,
                'latest': latest
            }
        
        return upload_status
    
    except Exception as e:
        print(f"⚠️ Could not fetch upload data: {e}")
        return {}

# ============================================
# EMAIL FUNCTIONS
# ============================================

def create_email_html(df, checklist_status={}, upload_status={}):
    """Create HTML email with Iron Lady branding"""
    
    # Calculate totals
    total_rms = int(df['Total_RMs'].sum())
    total_pitches = int(df['Total_Pitches'].sum())
    total_registrations = int(df['Total_Registrations'].sum())
    avg_conversion = round((total_registrations / total_pitches * 100), 1) if total_pitches > 0 else 0
    
    total_wa_audit = int(df['Total_WA_Audit'].sum())
    total_call_audit = int(df['Total_Call_Audit'].sum())
    total_mocks = int(df['Total_Mocks'].sum())
    total_sl_calls = int(df['Total_SL_Calls'].sum())
    total_current_mc = int(df['Total_Current_MC'].sum())
    
    # Create table rows for team performance
    table_rows = ""
    for _, row in df.iterrows():
        conversion = row.get('Conversion_Rate', 0)
        
        # Color code conversion rate
        if conversion >= 15:
            conv_color = IRONLADY_COLORS['success']
            conv_icon = '✅'
        elif conversion >= 10:
            conv_color = IRONLADY_COLORS['primary']
            conv_icon = '⚠️'
        else:
            conv_color = '#dc3545'
            conv_icon = '❌'
        
        table_rows += f"""
        <tr>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0;">{row['Team_Leader']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_RMs']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Pitches']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">{row['Total_Registrations']}</td>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e0e0e0; text-align: center;">
                {conv_icon} <span style="color: {conv_color}; font-weight: 700;">{conversion}%</span>
            </td>
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
        
        # Process checklist for each team leader in df
        for _, row in df.iterrows():
            username = row['username']
            team_name = row['Team_Leader']
            
            if username in checklist_status:
                status = checklist_status[username]
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
            else:
                # No checklist data for this user
                checklist_html += f"""
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{team_name}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;" colspan="4">
                                    <span style="color: #999;">No checklist data</span>
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
                    <p style="margin: 0;">ℹ️ No checklist data available for today. Team leaders should complete their daily checklists in the app.</p>
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
        
        # Process uploads for each team leader in df
        for _, row in df.iterrows():
            username = row['username']
            team_name = row['Team_Leader']
            
            if username in upload_status:
                status = upload_status[username]
                total_files = status['total_files']
                categories = ', '.join(status['categories'][:3])
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
            else:
                # No upload data for this user
                upload_html += f"""
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{team_name}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;" colspan="4">
                                    <span style="color: #999;">No uploads today</span>
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
                    <p style="margin: 0;">ℹ️ No upload data available for today. Team leaders should upload required documents in the app.</p>
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
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = ', '.join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_body, 'html'))
        
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
    
    # Check database file
    if not os.path.exists(DB_FILE):
        print(f"❌ Database file not found: {DB_FILE}")
        print("   Make sure the Streamlit app has been run and created the database")
        sys.exit(1)
    else:
        print(f"✅ Database file found: {DB_FILE}")
    
    print(f"📧 GMAIL_USER (sender): {'✅ Set' if EMAIL_SENDER else '❌ Missing'}")
    if EMAIL_SENDER:
        print(f"   → {EMAIL_SENDER}")
    print(f"🔑 GMAIL_APP_PASSWORD: {'✅ Set' if EMAIL_PASSWORD else '❌ Missing'}")
    if EMAIL_PASSWORD:
        print(f"   → {'*' * min(len(EMAIL_PASSWORD), 16)} (hidden)")
    print(f"📮 Recipients: {'✅ ' + str(len(RECIPIENT_EMAILS)) + ' email(s)' if RECIPIENT_EMAILS else '❌ None'}")
    if RECIPIENT_EMAILS:
        for email in RECIPIENT_EMAILS:
            print(f"   → {email}")
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
        sys.exit(1)
    
    print("\n✅ All configuration validated!")
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get team performance data
    print("\n" + "="*60)
    print(f"📊 FETCHING DATA FROM DATABASE ({today})")
    print("="*60)
    
    df = get_team_performance_data(today)
    
    if len(df) == 0:
        print("\n❌ NO DATA AVAILABLE!")
        print(f"   No performance data found for {today}")
        print("   Make sure team leaders have entered data in the Streamlit app")
        sys.exit(1)
    
    print(f"✅ Performance data loaded: {len(df)} team leaders")
    for _, row in df.iterrows():
        print(f"   → {row['Team_Leader']}: {row['Total_Pitches']} pitches, {row['Total_Registrations']} registrations ({row['Conversion_Rate']}%)")
    
    # Get checklist status
    print("\n" + "="*60)
    print("✅ FETCHING CHECKLIST STATUS")
    print("="*60)
    
    checklist_status = get_checklist_status(today)
    if checklist_status:
        print(f"✅ Checklist data loaded for {len(checklist_status)} team leaders")
        for username, status in checklist_status.items():
            print(f"   → {username}: {status['completed']}/{status['total']} tasks ({status['percentage']}%) - {status['day_type']}")
    else:
        print("ℹ️  No checklist data found for today")
    
    # Get upload status
    print("\n" + "="*60)
    print("📤 FETCHING UPLOAD STATUS")
    print("="*60)
    
    upload_status = get_upload_status(today)
    if upload_status:
        print(f"✅ Upload data loaded for {len(upload_status)} team leaders")
        for username, status in upload_status.items():
            print(f"   → {username}: {status['total_files']} files in {len(status['categories'])} categories")
    else:
        print("ℹ️  No upload data found for today")
    
    # Create email
    print("\n" + "="*60)
    print("📝 CREATING EMAIL")
    print("="*60)
    
    subject = f"Iron Lady Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_body = create_email_html(df, checklist_status, upload_status)
    
    print("✅ Email HTML created")
    print(f"   - Team performance: {len(df)} leaders")
    print(f"   - Checklist status: {len(checklist_status)} leaders")
    print(f"   - Upload status: {len(upload_status)} leaders")
    
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
        print(f"📧 Email sent to {len(RECIPIENT_EMAILS)} recipient(s)")
        for email in RECIPIENT_EMAILS:
            print(f"   ✓ {email}")
        print("\n🎉 Email automation completed successfully!")
    else:
        print("❌ FAILED!")
        print("="*60)
        print(f"Error: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
