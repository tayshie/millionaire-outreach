import smtplib
import sqlite3
import os
import time
import random
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

def get_settings():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    settings = {}
    for row in conn.execute('SELECT key, value FROM settings'):
        settings[row['key']] = row['value']
    conn.close()
    return settings

def inject_payment_links(text):
    s = get_settings()
    links = []
    if s.get('paypal_link'):
        links.append(f"PayPal: {s['paypal_link']}")
    if s.get('venmo_link'):
        links.append(f"Venmo: {s['venmo_link']}")
    if s.get('cashapp_link'):
        links.append(f"CashApp: {s['cashapp_link']}")
    if s.get('btc_address'):
        links.append(f"Bitcoin (BTC): {s['btc_address']}")
    if s.get('eth_address'):
        links.append(f"Ethereum (ETH): {s['eth_address']}")
    if s.get('sol_address'):
        links.append(f"Solana (SOL): {s['sol_address']}")
    payment_block = "\n".join(links) if links else ""
    return text.replace('{payment_links}', payment_block)

def send_email(sender_email, sender_password, smtp_server, smtp_port, use_tls, recipient, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg['X-Mailer'] = 'WealthOutreach/1.0'
    
    text_part = MIMEText(body, 'plain', 'utf-8')
    html = body.replace('\n', '<br>\n')
    html_part = MIMEText(f'<html><body>{html}</body></html>', 'html', 'utf-8')
    msg.attach(text_part)
    msg.attach(html_part)
    
    try:
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

def personalize_text(text, contact):
    replacements = {
        '{name}': contact['name'],
        '{rank}': str(contact.get('rank') or ''),
        '{net_worth}': str(contact.get('net_worth') or ''),
        '{source}': contact.get('source') or '',
        '{industry}': contact.get('industry') or '',
        '{country}': contact.get('country') or '',
        '{company}': contact.get('company') or '',
        '{amount}': '5',
        '{tier}': contact.get('wealth_tier') or 'wealthy individual',
    }
    for key, val in replacements.items():
        text = text.replace(key, val)
    return text

def run_campaign(campaign_id, delay_min=10, delay_max=60):
    settings = get_settings()
    sender = settings.get('smtp_email', '')
    password = settings.get('smtp_password', '')
    server = settings.get('smtp_server', 'smtp.gmail.com')
    port = int(settings.get('smtp_port', 587))
    use_tls = settings.get('smtp_use_tls', 'true').lower() == 'true'
    daily_limit = int(settings.get('daily_limit', '100'))
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    if not campaign:
        conn.close()
        return {'error': 'Campaign not found'}
    
    try:
        follow_ups = json.loads(campaign['follow_ups']) if campaign.get('follow_ups') else []
    except:
        follow_ups = []
    
    all_emails = [{'subject': campaign['subject'], 'body': campaign['body'], 'delay_days': 0}]
    all_emails.extend(follow_ups)
    
    today_sent = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status='sent' AND date(sent_at) = date('now')"
    ).fetchone()[0]
    
    remaining_today = max(0, daily_limit - today_sent)
    
    contacts = conn.execute(
        '''SELECT c.* FROM contacts c 
           LEFT JOIN messages m ON m.contact_id = c.id AND m.campaign_id = ? AND m.step_index = 0
           WHERE m.id IS NULL AND c.email IS NOT NULL AND c.email != "" 
           AND c.status != 'skipped'
           ORDER BY c.net_worth DESC
           LIMIT ?''',
        (campaign_id, remaining_today)
    ).fetchall()
    
    if not contacts:
        conn.execute('UPDATE campaigns SET status = ? WHERE id = ?', ('completed', campaign_id))
        conn.commit()
        conn.close()
        return {'sent': 0, 'failed': 0, 'message': 'No contacts to send to (all already contacted or daily limit reached)'}
    
    conn.execute('UPDATE campaigns SET status = ? WHERE id = ?', ('running', campaign_id))
    conn.commit()
    
    sent = 0
    failed = 0
    
    for contact in contacts:
        email_data = all_emails[0]
        subject = personalize_text(email_data['subject'], contact)
        body = personalize_text(email_data['body'], contact)
        body = inject_payment_links(body)
        subject = inject_payment_links(subject)
        
        success, error = send_email(sender, password, server, port, use_tls,
                                     contact['email'], subject, body)
        
        if success:
            conn.execute(
                'INSERT INTO messages (campaign_id, contact_id, recipient, subject, body, sent_at, status, step_index) VALUES (?,?,?,?,?,?,?,?)',
                (campaign_id, contact['id'], contact['email'], subject, body, datetime.now(), 'sent', 0)
            )
            conn.execute("UPDATE contacts SET status='contacted', updated_at=? WHERE id=?", (datetime.now(), contact['id']))
            sent += 1
        else:
            conn.execute(
                'INSERT INTO messages (campaign_id, contact_id, recipient, subject, body, status, step_index) VALUES (?,?,?,?,?,?,?)',
                (campaign_id, contact['id'], contact['email'], subject, body, f'failed: {error}', 0)
            )
            failed += 1
        
        conn.execute('UPDATE campaigns SET sent_count = sent_count + 1 WHERE id = ?', (campaign_id,))
        conn.commit()
        
        if delay_min > 0 or delay_max > 0:
            delay = random.randint(delay_min, delay_max)
            if delay > 0:
                time.sleep(delay)
    
    conn.execute('UPDATE campaigns SET status = ? WHERE id = ?', ('active', campaign_id))
    conn.commit()
    
    total_sent = conn.execute('SELECT sent_count FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()['sent_count']
    conn.close()
    
    return {'sent': sent, 'failed': failed, 'total_sent': total_sent, 'follow_ups': len(follow_ups)}

def send_follow_ups(campaign_id, batch_size=50):
    """Send follow-up emails that are due."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    if not campaign:
        conn.close()
        return {'error': 'Campaign not found'}
    
    try:
        follow_ups = json.loads(campaign['follow_ups']) if campaign.get('follow_ups') else []
    except:
        follow_ups = []
    
    if not follow_ups:
        conn.close()
        return {'sent': 0, 'message': 'No follow-ups configured'}
    
    settings = get_settings()
    sender = settings.get('smtp_email', '')
    password = settings.get('smtp_password', '')
    server = settings.get('smtp_server', 'smtp.gmail.com')
    port = int(settings.get('smtp_port', 587))
    use_tls = settings.get('smtp_use_tls', 'true').lower() == 'true'
    
    sent = 0
    for step_idx, follow_up in enumerate(follow_ups):
        step_index = step_idx + 1
        delay_days = follow_up.get('delay_days', 3)
        
        # Find contacts who received the previous step but not this one
        prev_step = step_index - 1
        due_date = datetime.now() - timedelta(days=delay_days)
        
        contacts = conn.execute(
            '''SELECT c.* FROM contacts c
               JOIN messages pm ON pm.contact_id = c.id AND pm.campaign_id = ? AND pm.step_index = ? AND pm.status = 'sent'
               LEFT JOIN messages nm ON nm.contact_id = c.id AND nm.campaign_id = ? AND nm.step_index = ?
               WHERE nm.id IS NULL AND c.status != 'skipped'
               AND pm.sent_at <= ?
               ORDER BY c.net_worth DESC
               LIMIT ?''',
            (campaign_id, prev_step, campaign_id, step_index, due_date, batch_size)
        ).fetchall()
        
        for contact in contacts:
            subject = personalize_text(follow_up['subject'], contact)
            body = personalize_text(follow_up['body'], contact)
            body = inject_payment_links(body)
            subject = inject_payment_links(subject)
            
            success, error = send_email(sender, password, server, port, use_tls,
                                         contact['email'], subject, body)
            
            if success:
                conn.execute(
                    'INSERT INTO messages (campaign_id, contact_id, recipient, subject, body, sent_at, status, step_index) VALUES (?,?,?,?,?,?,?,?)',
                    (campaign_id, contact['id'], contact['email'], subject, body, datetime.now(), 'sent', step_index)
                )
                sent += 1
            
            conn.execute('UPDATE campaigns SET sent_count = sent_count + 1 WHERE id = ?', (campaign_id,))
            conn.commit()
            time.sleep(random.randint(5, 15))
    
    conn.close()
    return {'sent': sent, 'remaining_steps': len(follow_ups)}
