"""
IRON LADY - OFFICIAL BRANDED DAILY EMAIL REPORT
Enhanced HTML email with official Iron Lady branding
Scheduled for 7:00 PM IST Daily
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

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

MAX_EMAIL_SIZE_MB = 20

# ============================================
# UTILITY FUNCTIONS
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
    <table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: white; border-radius: 0px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <thead>
            <tr style="background: {IRONLADY_COLORS['dark']};">
                <th style="padding: 18px; text-align: left; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Team Leader</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">RMs Active</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Pitches</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Registrations</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Conversion</th>
                <th style="padding: 18px; text-align: center; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Status</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, lead in enumerate(team_data):
        bg_color = IRONLADY_COLORS['light'] if idx % 2 == 0 else 'white'
        conversion = float(lead.get('conversion', 0))
        status_text, status_color, status_icon = get_performance_status(conversion)
        
        html += f"""
        <tr style="background: {bg_color}; border-bottom: 2px solid {IRONLADY_COLORS['accent']};">
            <td style="padding: 18px; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">{lead.get('name', 'Unknown')}</td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']}; font-weight: 600;">{lead.get('rms', 0)}</td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']};">
                <span style="font-weight: 900; font-size: 1.1rem;">{lead.get('pitches_actual', 0)}</span>/{lead.get('pitches_target', 0)}
            </td>
            <td style="padding: 18px; text-align: center; color: {IRONLADY_COLORS['dark']};">
                <span style="font-weight: 900; font-size: 1.1rem;">{lead.get('reg_actual', 0)}</span>/{lead.get('reg_target', 0)}
            </td>
            <td style="padding: 18px; text-align: center; color: {status_color}; font-weight: 900; font-size: 1.2rem;">
                {conversion:.1f}%
            </td>
            <td style="padding: 18px; text-align: center;">
                <span style="background: {status_color}; color: white; padding: 8px 16px; border-radius: 0px; font-weight: 700; font-size: 0.85rem; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px;">
                    {status_icon} {status_text}
                </span>
            </td>
        </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html

def generate_email_html(report_data=None):
    today = datetime.now()
    formatted_date = today.strftime('%A, %B %d, %Y')
    formatted_time = today.strftime('%I:%M %p IST')
    
    if report_data is None:
        report_data = {
            'total_leads': 150,
            'pitch_target': 50,
            'pitch_actual': 45,
            'pitch_achievement': 90.0,
            'reg_target': 40,
            'reg_actual': 35,
            'reg_achievement': 87.5,
            'conversion_rate': 77.8,
            'team_leads': [
                {'name': 'Priya Sharma', 'rms': 5, 'pitches_target': 30, 'pitches_actual': 28, 'reg_target': 22, 'reg_actual': 20, 'conversion': 71.4},
                {'name': 'Rahul Mehta', 'rms': 4, 'pitches_target': 15, 'pitches_actual': 13, 'reg_target': 12, 'reg_actual': 11, 'conversion': 84.6},
                {'name': 'Anjali Desai', 'rms': 3, 'pitches_target': 10, 'pitches_actual': 9, 'reg_target': 8, 'reg_actual': 6, 'conversion': 66.7},
            ]
        }
    
    overall_status, overall_color, overall_icon = get_performance_status(report_data['conversion_rate'])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Iron Lady Daily Report</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background: {IRONLADY_COLORS['light']};">
        <div style="max-width: 800px; margin: 0 auto; background: {IRONLADY_COLORS['light']}; padding: 20px;">
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 40px 30px; text-align: center; margin-bottom: 30px; border-top: 8px solid {IRONLADY_COLORS['primary']}; border-bottom: 8px solid {IRONLADY_COLORS['primary']};">
                <h1 style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 3rem; font-weight: 900; letter-spacing: 3px;">
                    IRON LADY
                </h1>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 15px 0 0 0; font-size: 1rem;">
                    Sales Performance Management System
                </p>
                <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 120px; margin: 25px auto;"></div>
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 20px 0 5px 0; font-size: 1.5rem; font-weight: 900;">
                    DAILY PERFORMANCE REPORT
                </h2>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 1rem; font-weight: 600;">
                    {formatted_date}
                </p>
            </div>
            
            <div style="background: white; padding: 30px; margin-bottom: 25px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 25px 0; font-size: 1.5rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px;">
                    EXECUTIVE SUMMARY
                </h2>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <tr>
                        <td style="width: 50%; padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                            <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600;">Total Leads</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['primary']}; font-size: 2.5rem; font-weight: 900;">
                                {report_data['total_leads']}
                            </p>
                            <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">Active Prospects</p>
                        </td>
                        <td style="width: 50%; padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['success']};">
                            <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600;">Pitch Achievement</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['success']}; font-size: 2.5rem; font-weight: 900;">
                                {report_data['pitch_achievement']:.0f}%
                            </p>
                            <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">
                                {report_data['pitch_actual']}/{report_data['pitch_target']} Completed
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {IRONLADY_COLORS['warning']};">
                            <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600;">Registration Achievement</p>
                            <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['warning']}; font-size: 2.5rem; font-weight: 900;">
                                {report_data['reg_achievement']:.0f}%
                            </p>
                            <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">
                                {report_data['reg_actual']}/{report_data['reg_target']} Completed
                            </p>
                        </td>
                        <td style="padding: 20px; background: {IRONLADY_COLORS['light']}; border-left: 6px solid {overall_color};">
                            <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600;">Conversion Rate</p>
                            <p style="margin: 10px 0 0 0; color: {overall_color}; font-size: 2.5rem; font-weight: 900;">
                                {report_data['conversion_rate']:.1f}%
                            </p>
                            <p style="margin: 8px 0 0 0;">
                                <span style="background: {overall_color}; color: white; padding: 6px 14px; font-weight: 700; font-size: 0.8rem;">
                                    {overall_icon} {overall_status}
                                </span>
                            </p>
                        </td>
                    </tr>
                </table>
                
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-left: 6px solid {overall_color};">
                    <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700; font-size: 1.1rem;">
                        {overall_icon} Overall Status: {overall_status}
                    </p>
                    <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['dark']};">
                        Team is {'performing excellently' if report_data['conversion_rate'] >= 90 else 'meeting expectations' if report_data['conversion_rate'] >= 75 else 'showing room for improvement'}. 
                        {'Continue the great work!' if report_data['conversion_rate'] >= 75 else 'Focus on improving conversion strategies.'}
                    </p>
                </div>
            </div>
            
            <div style="background: white; padding: 30px; margin-bottom: 25px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; font-size: 1.5rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px;">
                    TEAM LEADER PERFORMANCE
                </h2>
                {generate_team_lead_table(report_data.get('team_leads', []))}
            </div>
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 25px; text-align: center; border-top: 5px solid {IRONLADY_COLORS['primary']}; border-bottom: 5px solid {IRONLADY_COLORS['primary']};">
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 10px 0; font-weight: 900; font-size: 1.3rem; letter-spacing: 2px;">
                    IRON LADY
                </p>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 0.9rem; font-weight: 600;">
                    Sales Performance Management System
                </p>
                <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 100px; margin: 15px auto;"></div>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 0.8rem;">
                    Automated Daily Report - Generated at {formatted_time}
                </p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html

def send_daily_email(report_data=None):
    sender_email = os.environ.get('GMAIL_USER')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    recipient_email = os.environ.get('CEO_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ Missing email configuration")
        return False
    
    try:
        html_content = generate_email_html(report_data)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            
            msg = f"From: {sender_email}\r\n"
            msg += f"To: {recipient_email}\r\n"
            msg += f"Subject: Iron Lady Daily Report | {datetime.now().strftime('%B %d, %Y')}\r\n"
            msg += "Content-Type: text/html; charset=utf-8\r\n"
            msg += "\r\n"
            msg += html_content
            
            server.sendmail(sender_email, recipient_email, msg.encode('utf-8'))
        
        print(f"✅ Email sent successfully to {recipient_email}")
        print(f"🕐 Sent at: {datetime.now().strftime('%I:%M %p IST')}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check Gmail credentials.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IRON LADY - Official Daily Email Report")
    print("=" * 60)
    print(f"🕐 Execution time: {datetime.now().strftime('%I:%M %p IST on %B %d, %Y')}")
    print()
    
    print("📊 Generating report...")
    success = send_daily_email(report_data=None)
    
    print()
    if success:
        print("🎉 Daily email sent successfully!")
    else:
        print("❌ Failed to send email.")
    print("=" * 60)
