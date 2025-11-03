"""
IRON LADY - OFFICIAL BRANDED DAILY EMAIL REPORT
Enhanced HTML email with official Iron Lady branding
Scheduled for 7:00 PM IST Daily
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import os
import json
import pandas as pd

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

def truncate_text(text, max_chars=5000):
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... (content truncated for email size limit)"

def get_performance_status(percentage):
    if percentage >= 90:
        return "Excellent", IRONLADY_COLORS['success'], "🎯"
    elif percentage >= 75:
        return "Good", IRONLADY_COLORS['warning'], "✅"
    elif percentage >= 60:
        return "Fair", IRONLADY_COLORS['warning'], "⚠️"
    else:
        return "Needs Attention", IRONLADY_COLORS['danger'], "❌"

def generate_ocr_summary_html(ocr_results):
    if not ocr_results:
        return ""
    
    html = f"""
    <div style="background: white; padding: 25px; border-radius: 0px; margin: 25px 0; border-left: 6px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; font-size: 1.5rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['accent']}; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">
            🤖 AI-POWERED DOCUMENT ANALYSIS
        </h2>
    """
    
    total_files = len(ocr_results)
    total_text = sum(len(data.get('text', '')) for data in ocr_results.values())
    
    html += f"""
    <div style="background: {IRONLADY_COLORS['light']}; padding: 20px; border-radius: 0px; margin: 15px 0;">
        <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700; font-size: 1rem; text-transform: uppercase;">📊 Analysis Summary</p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
            <div>
                <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.7; font-size: 0.85rem;">Files Processed</p>
                <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['primary']}; font-size: 1.5rem; font-weight: 900;">{total_files}</p>
            </div>
            <div>
                <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.7; font-size: 0.85rem;">Text Extracted</p>
                <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['primary']}; font-size: 1.5rem; font-weight: 900;">{total_text:,} chars</p>
            </div>
        </div>
    </div>
    """
    
    file_count = 0
    for file_key, data in ocr_results.items():
        if file_count >= 5:
            html += f"""
            <div style="background: {IRONLADY_COLORS['light']}; padding: 15px; border-radius: 0px; text-align: center; margin: 15px 0;">
                <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-style: italic;">
                    ... and {len(ocr_results) - 5} more files. View complete analysis in the dashboard.
                </p>
            </div>
            """
            break
        
        file_name = data.get('file_name', 'Unknown')
        text = data.get('text', '')
        entities = data.get('entities', {})
        metrics = data.get('metrics', {})
        
        html += f"""
        <div style="background: white; border: 3px solid {IRONLADY_COLORS['accent']}; padding: 20px; margin: 20px 0; border-radius: 0px;">
            <h4 style="color: {IRONLADY_COLORS['primary']}; margin: 0 0 15px 0; font-weight: 700; text-transform: uppercase;">📄 {file_name}</h4>
        """
        
        if text:
            truncated_text = truncate_text(text, 500)
            html += f"""
            <div style="margin: 15px 0;">
                <p style="margin: 0 0 10px 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">Extracted Content:</p>
                <pre style="background: {IRONLADY_COLORS['light']}; padding: 15px; border-radius: 0px; font-size: 0.85rem; overflow-x: auto; white-space: pre-wrap; color: {IRONLADY_COLORS['dark']}; margin: 0; font-family: 'Courier New', monospace;">{truncated_text}</pre>
            </div>
            """
        
        if 'error' not in entities:
            has_entities = any(entities.values())
            if has_entities:
                html += f"""
                <div style="margin: 15px 0;">
                    <p style="margin: 0 0 10px 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">Identified Entities:</p>
                    <ul style="margin: 0; padding-left: 20px; color: {IRONLADY_COLORS['dark']};">
                """
                for entity_type, values in entities.items():
                    if values:
                        unique_values = list(set(values))[:5]
                        html += f"<li><strong>{entity_type}:</strong> {', '.join(unique_values)}</li>"
                html += "</ul></div>"
        
        if metrics:
            html += f"""
            <div style="margin: 15px 0;">
                <p style="margin: 0 0 10px 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">Key Metrics Extracted:</p>
                <ul style="margin: 0; padding-left: 20px; color: {IRONLADY_COLORS['dark']};">
            """
            if metrics.get('numbers_found'):
                html += f"<li><strong>Numbers:</strong> {', '.join(metrics['numbers_found'][:10])}</li>"
            if metrics.get('potential_leads'):
                html += f"<li><strong>Potential Leads:</strong> {', '.join(metrics['potential_leads'])}</li>"
            if metrics.get('potential_registrations'):
                html += f"<li><strong>Potential Registrations:</strong> {', '.join(metrics['potential_registrations'])}</li>"
            html += "</ul></div>"
        
        html += "</div>"
        file_count += 1
    
    html += "</div>"
    return html

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

def generate_checklist_html(checklist_data):
    if not checklist_data:
        return ""
    
    completed = sum(1 for item in checklist_data if item.get('completed', False))
    total = len(checklist_data)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    html = f"""
    <div style="background: white; padding: 25px; border-radius: 0px; margin: 25px 0; border-left: 6px solid {IRONLADY_COLORS['primary']}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; font-size: 1.5rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['accent']}; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">
            ✅ DAILY CHECKLIST COMPLETION
        </h2>
        
        <div style="background: {IRONLADY_COLORS['light']}; padding: 20px; border-radius: 0px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: {IRONLADY_COLORS['dark']}; font-weight: 700; text-transform: uppercase;">Overall Progress</span>
                <span style="color: {IRONLADY_COLORS['primary']}; font-weight: 900; font-size: 1.3rem;">{completion_rate:.0f}%</span>
            </div>
            <div style="background: white; height: 35px; border-radius: 0px; overflow: hidden; position: relative; border: 2px solid {IRONLADY_COLORS['dark']};">
                <div style="background: {IRONLADY_COLORS['primary']}; height: 100%; width: {completion_rate}%; transition: width 0.3s;"></div>
                <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: {'white' if completion_rate > 50 else IRONLADY_COLORS['dark']}; font-weight: 900; font-size: 1rem;">
                    {completed}/{total} Tasks
                </span>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
    """
    
    for item in checklist_data:
        task_name = item.get('task', 'Unknown Task')
        is_completed = item.get('completed', False)
        priority = item.get('priority', 'medium')
        
        if is_completed:
            bg_color = '#d4edda'
            border_color = IRONLADY_COLORS['success']
            icon = '✅'
        else:
            if priority == 'high':
                bg_color = '#f8d7da'
                border_color = IRONLADY_COLORS['danger']
                icon = '❌'
            else:
                bg_color = '#fff3cd'
                border_color = IRONLADY_COLORS['warning']
                icon = '⏳'
        
        html += f"""
        <div style="background: {bg_color}; border-left: 5px solid {border_color}; padding: 14px 18px; margin: 10px 0; border-radius: 0px; display: flex; align-items: center;">
            <span style="font-size: 1.3rem; margin-right: 12px;">{icon}</span>
            <span style="color: {IRONLADY_COLORS['dark']}; font-weight: 600; font-size: 0.95rem;">{task_name}</span>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html

def generate_email_html(report_data=None, ocr_results=None):
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
            ],
            'checklist': [
                {'task': 'WA Audit - Minimum 10', 'completed': True, 'priority': 'high'},
                {'task': 'SL Calls - 5', 'completed': True, 'priority': 'high'},
                {'task': 'Call Audit - Minimum 5 calls', 'completed': True, 'priority': 'medium'},
                {'task': 'CRM Updated', 'completed': True, 'priority': 'high'},
                {'task': 'Hot prospects list shared', 'completed': True, 'priority': 'high'},
                {'task': 'Follow up calls - 2 Registrations', 'completed': False, 'priority': 'high'},
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
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: {IRONLADY_COLORS['light']};
            }}
        </style>
    </head>
    <body>
        <div style="max-width: 800px; margin: 0 auto; background: {IRONLADY_COLORS['light']}; padding: 20px;">
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 40px 30px; border-radius: 0px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 30px; border-top: 8px solid {IRONLADY_COLORS['primary']}; border-bottom: 8px solid {IRONLADY_COLORS['primary']};">
                <h1 style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 3.5rem; font-weight: 900; letter-spacing: 3px; text-transform: uppercase;">
                    IRON LADY
                </h1>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 15px 0 0 0; font-size: 1.1rem; letter-spacing: 1px; font-weight: 400;">
                    Sales Performance Management System
                </p>
                <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 120px; margin: 25px auto;"></div>
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 20px 0 5px 0; font-size: 1.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">
                    📊 DAILY PERFORMANCE REPORT
                </h2>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 1rem; font-weight: 600;">
                    {formatted_date}
                </p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 25px 0; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">
                    📈 EXECUTIVE SUMMARY
                </h2>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 25px;">
                    
                    <div style="background: {IRONLADY_COLORS['light']}; padding: 22px; border-radius: 0px; border-left: 6px solid {IRONLADY_COLORS['primary']};">
                        <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">Total Leads</p>
                        <p style="margin: 12px 0 0 0; color: {IRONLADY_COLORS['primary']}; font-size: 2.8rem; font-weight: 900; line-height: 1;">
                            {report_data['total_leads']}
                        </p>
                        <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">Active Prospects</p>
                    </div>
                    
                    <div style="background: {IRONLADY_COLORS['light']}; padding: 22px; border-radius: 0px; border-left: 6px solid {IRONLADY_COLORS['success']};">
                        <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">Pitch Achievement</p>
                        <p style="margin: 12px 0 0 0; color: {IRONLADY_COLORS['success']}; font-size: 2.8rem; font-weight: 900; line-height: 1;">
                            {report_data['pitch_achievement']:.0f}%
                        </p>
                        <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">
                            {report_data['pitch_actual']}/{report_data['pitch_target']} Completed
                        </p>
                    </div>
                    
                    <div style="background: {IRONLADY_COLORS['light']}; padding: 22px; border-radius: 0px; border-left: 6px solid {IRONLADY_COLORS['warning']};">
                        <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">Registration Achievement</p>
                        <p style="margin: 12px 0 0 0; color: {IRONLADY_COLORS['warning']}; font-size: 2.8rem; font-weight: 900; line-height: 1;">
                            {report_data['reg_achievement']:.0f}%
                        </p>
                        <p style="margin: 5px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.6; font-size: 0.85rem;">
                            {report_data['reg_actual']}/{report_data['reg_target']} Completed
                        </p>
                    </div>
                    
                    <div style="background: {IRONLADY_COLORS['light']}; padding: 22px; border-radius: 0px; border-left: 6px solid {overall_color};">
                        <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">Conversion Rate</p>
                        <p style="margin: 12px 0 0 0; color: {overall_color}; font-size: 2.8rem; font-weight: 900; line-height: 1;">
                            {report_data['conversion_rate']:.1f}%
                        </p>
                        <p style="margin: 8px 0 0 0;">
                            <span style="background: {overall_color}; color: white; padding: 6px 14px; border-radius: 0px; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                {overall_icon} {overall_status}
                            </span>
                        </p>
                    </div>
                    
                </div>
                
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-radius: 0px; border-left: 6px solid {overall_color};">
                    <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700; font-size: 1.1rem; text-transform: uppercase;">
                        {overall_icon} <strong>Overall Status:</strong> {overall_status}
                    </p>
                    <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['dark']}; opacity: 0.8; font-size: 0.95rem;">
                        Team is {'performing excellently' if report_data['conversion_rate'] >= 90 else 'meeting expectations' if report_data['conversion_rate'] >= 75 else 'showing room for improvement'}. 
                        {'Continue the great work!' if report_data['conversion_rate'] >= 75 else 'Focus on improving conversion strategies.'}
                    </p>
                </div>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">
                    👥 TEAM LEADER PERFORMANCE
                </h2>
                {generate_team_lead_table(report_data.get('team_leads', []))}
            </div>
            
            {generate_checklist_html(report_data.get('checklist', []))}
            
            {generate_ocr_summary_html(ocr_results)}
            
            <div style="background: white; padding: 30px; border-radius: 0px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 6px solid {IRONLADY_COLORS['primary']};">
                <h2 style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 20px 0; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid {IRONLADY_COLORS['primary']}; padding-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">
                    🎯 KEY ACTION ITEMS
                </h2>
                
                <div style="background: {IRONLADY_COLORS['light']}; padding: 20px; border-radius: 0px; margin: 15px 0;">
                    <h3 style="color: {IRONLADY_COLORS['primary']}; margin: 0 0 15px 0; font-size: 1.1rem; font-weight: 900; text-transform: uppercase;">Priority Actions for Tomorrow:</h3>
                    <ul style="margin: 0; padding-left: 20px; color: {IRONLADY_COLORS['dark']}; line-height: 1.9;">
                        <li style="margin-bottom: 8px;"><strong>Follow-up Calls:</strong> Complete pending registrations from last masterclass</li>
                        <li style="margin-bottom: 8px;"><strong>CRM Updates:</strong> Ensure all attendance and registrations are recorded</li>
                        <li style="margin-bottom: 8px;"><strong>Hot Prospects:</strong> Focus on high-potential leads identified today</li>
                        <li><strong>Call Quality:</strong> Review call audit feedback for performance improvement</li>
                    </ul>
                </div>
                
                <div style="background: {IRONLADY_COLORS['accent']}; padding: 20px; border-radius: 0px; border-left: 6px solid {IRONLADY_COLORS['warning']}; margin: 15px 0;">
                    <p style="margin: 0; color: {IRONLADY_COLORS['dark']}; font-weight: 700;">💡 <strong>PERFORMANCE INSIGHT:</strong></p>
                    <p style="margin: 10px 0 0 0; color: {IRONLADY_COLORS['dark']};">
                        {'Teams showing excellent conversion rates should maintain momentum and share best practices.' if report_data['conversion_rate'] >= 75 else 'Consider additional training sessions and peer mentoring to improve conversion rates.'}
                    </p>
                </div>
            </div>
            
            <div style="background: {IRONLADY_COLORS['primary']}; padding: 25px; border-radius: 0px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <p style="color: white; margin: 0 0 15px 0; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                    📊 ACCESS COMPLETE DASHBOARD
                </p>
                <p style="color: rgba(255,255,255,0.9); margin: 0 0 20px 0; font-size: 0.95rem;">
                    View detailed analytics, team metrics, and real-time updates
                </p>
                <a href="YOUR_STREAMLIT_APP_URL" style="background: white; color: {IRONLADY_COLORS['primary']}; padding: 14px 32px; border-radius: 0px; text-decoration: none; font-weight: 900; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.2); text-transform: uppercase; letter-spacing: 1px;">
                    OPEN DASHBOARD →
                </a>
            </div>
            
            <div style="background: {IRONLADY_COLORS['accent']}; padding: 25px; border-radius: 0px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 5px solid {IRONLADY_COLORS['primary']}; border-bottom: 5px solid {IRONLADY_COLORS['primary']};">
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0 0 10px 0; font-weight: 900; font-size: 1.3rem; text-transform: uppercase; letter-spacing: 2px;">
                    IRON LADY
                </p>
                <p style="color: {IRONLADY_COLORS['dark']}; margin: 0; font-size: 0.9rem; font-weight: 600;">
                    Sales Performance Management System | Official Branded Edition
                </p>
                <div style="background: {IRONLADY_COLORS['primary']}; height: 3px; width: 100px; margin: 15px auto;"></div>
                <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.7; margin: 0; font-size: 0.8rem;">
                    📧 Automated Daily Report | Generated at {formatted_time}
                </p>
                <p style="color: {IRONLADY_COLORS['dark']}; opacity: 0.6; margin: 10px 0 0 0; font-size: 0.75rem;">
                    © 2024 Iron Lady. All rights reserved. | Email optimized (< {MAX_EMAIL_SIZE_MB}MB)
                </p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html

def send_daily_email(report_data=None, ocr_results=None):
    sender_email = os.environ.get('GMAIL_USER')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    recipient_email = os.environ.get('CEO_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ Missing email configuration in environment variables")
        print("Required: GMAIL_USER, GMAIL_APP_PASSWORD, CEO_EMAIL")
        return False
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Iron Lady Daily Report | {datetime.now().strftime('%B %d, %Y')} - Performance Summary"
    message["From"] = sender_email
    message["To"] = recipient_email
    
    html_content = generate_email_html(report_data, ocr_results)
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        email_size = len(message.as_string())
        email_size_mb = email_size / (1024 * 1024)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print(f"✅ Iron Lady branded email sent successfully to {recipient_email}")
        print(f"📊 Email size: {email_size_mb:.2f}MB")
        print(f"🕐 Sent at: {datetime.now().strftime('%I:%M %p IST')}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your Gmail credentials.")
        print("💡 Tip: Make sure you're using an App Password, not your regular Gmail password.")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending email: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IRON LADY - Official Branded Daily Email Report")
    print("=" * 60)
    print(f"🕐 Execution time: {datetime.now().strftime('%I:%M %p IST on %B %d, %Y')}")
    print()
    
    print("📊 Generating Iron Lady branded report...")
    success = send_daily_email(report_data=None, ocr_results=None)
    
    print()
    if success:
        print("🎉 Daily email report sent successfully!")
    else:
        print("❌ Failed to send daily email report.")
    print("=" * 60)
