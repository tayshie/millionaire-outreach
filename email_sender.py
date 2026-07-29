import smtplib
import sqlite3
import os
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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
    
    today_sent = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status='sent' AND date(sent_at) = date('now')"
    ).fetchone()[0]
    
    remaining_today = max(0, daily_limit - today_sent)
    
    contacts = conn.execute(
        '''SELECT c.* FROM contacts c 
           LEFT JOIN messages m ON m.contact_id = c.id AND m.campaign_id = ? 
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
        subject = campaign['subject']
        body = campaign['body']
        
        replacements = {
            '{name}': contact['name'],
            '{rank}': str(contact['rank'] or ''),
            '{net_worth}': str(contact['net_worth'] or ''),
            '{source}': contact['source'] or '',
            '{industry}': contact['industry'] or '',
            '{country}': contact['country'] or '',
            '{company}': contact['company'] or '',
            '{amount}': '5',
            '{tier}': contact['wealth_tier'] or 'wealthy individual',
        }
        for key, val in replacements.items():
            subject = subject.replace(key, val)
            body = body.replace(key, val)
        
        body = inject_payment_links(body)
        subject = inject_payment_links(subject)
        
        success, error = send_email(sender, password, server, port, use_tls,
                                     contact['email'], subject, body)
        
        if success:
            conn.execute(
                'INSERT INTO messages (campaign_id, contact_id, recipient, subject, body, sent_at, status) VALUES (?,?,?,?,?,?,?)',
                (campaign_id, contact['id'], contact['email'], subject, body, datetime.now(), 'sent')
            )
            conn.execute("UPDATE contacts SET status='contacted', updated_at=? WHERE id=?", (datetime.now(), contact['id']))
            sent += 1
        else:
            conn.execute(
                'INSERT INTO messages (campaign_id, contact_id, recipient, subject, body, status) VALUES (?,?,?,?,?,?)',
                (campaign_id, contact['id'], contact['email'], subject, body, f'failed: {error}')
            )
            failed += 1
        
        conn.execute('UPDATE campaigns SET sent_count = sent_count + 1 WHERE id = ?', (campaign_id,))
        conn.commit()
        
        if delay_min > 0 or delay_max > 0:
            delay = random.randint(delay_min, delay_max)
            if delay > 0:
                time.sleep(delay)
    
    conn.execute('UPDATE campaigns SET status = ? WHERE id = ?', ('completed', campaign_id))
    conn.commit()
    
    total_sent = conn.execute('SELECT sent_count FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()['sent_count']
    conn.close()
    
    return {'sent': sent, 'failed': failed, 'total_sent': total_sent}
