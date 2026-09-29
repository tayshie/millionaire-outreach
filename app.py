from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
import json
import csv
import io
from datetime import datetime
from models import init_db, seed_templates, seed_sample_contacts, get_db
from scraper import run_scrape_all, run_scrape_source, import_csv_data, save_contacts
from contact_finder import find_contact_info_batch, find_emails_for_contact
from email_sender import run_campaign, get_settings

app = Flask(__name__)
app.secret_key = 'millionaire-outreach-secret-key-change-me'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

init_db()
seed_templates()
seed_sample_contacts()

def inject_payment_links(text):
    """Replace {payment_links} with configured payment methods."""
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
    payment_block = "\n".join(links) if links else "[Configure payment methods in Settings to enable {payment_links}]"
    return text.replace('{payment_links}', payment_block)

@app.route('/')
def index():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    billionaires = conn.execute("SELECT COUNT(*) FROM contacts WHERE wealth_tier='billionaire'").fetchone()[0]
    millionaires = conn.execute("SELECT COUNT(*) FROM contacts WHERE wealth_tier IN ('millionaire','multi-millionaire','centi-millionaire')").fetchone()[0]
    with_email = conn.execute('SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ""').fetchone()[0]
    emailed = conn.execute('SELECT COUNT(DISTINCT contact_id) FROM messages WHERE status="sent"').fetchone()[0]
    campaigns = conn.execute('SELECT COUNT(*) FROM campaigns').fetchone()[0]
    donations = conn.execute('SELECT COALESCE(SUM(donated_amount), 0) FROM messages WHERE donated_amount IS NOT NULL').fetchone()[0]
    conn.close()
    return render_template('index.html', total=total, billionaires=billionaires,
                          millionaires=millionaires, with_email=with_email,
                          emailed=emailed, campaigns=campaigns, donations=donations)

@app.route('/contacts')
def contacts():
    conn = get_db()
    tier = request.args.get('tier', '')
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    country = request.args.get('country', '')
    
    query = 'SELECT * FROM contacts WHERE 1=1'
    params = []
    if tier:
        query += ' AND wealth_tier = ?'
        params.append(tier)
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    if search:
        query += ' AND (name LIKE ? OR company LIKE ? OR industry LIKE ? OR country LIKE ?)'
        s = f'%{search}%'
        params.extend([s, s, s, s])
    if country:
        query += ' AND country = ?'
        params.append(country)
    query += ' ORDER BY net_worth DESC'
    
    contacts_list = conn.execute(query, params).fetchall()
    countries = conn.execute('SELECT DISTINCT country FROM contacts WHERE country IS NOT NULL AND country != "" ORDER BY country').fetchall()
    conn.close()
    return render_template('contacts.html', contacts=contacts_list, countries=countries,
                          current_tier=tier, current_status=status_filter, current_country=country)

@app.route('/api/contacts')
def api_contacts():
    conn = get_db()
    contacts_list = [dict(r) for r in conn.execute('SELECT * FROM contacts ORDER BY net_worth DESC').fetchall()]
    conn.close()
    return jsonify(contacts_list)

@app.route('/api/contacts/<int:id>', methods=['GET', 'PUT'])
def api_contact(id):
    conn = get_db()
    if request.method == 'PUT':
        data = request.json
        conn.execute(
            '''UPDATE contacts SET name=?, net_worth=?, wealth_tier=?, email=?, phone=?, company=?, title=?,
               country=?, state=?, city=?, industry=?, source=?, linkedin_url=?, website_url=?,
               notes=?, tags=?, status=?, twitter_handle=?, instagram_handle=?,
               annual_revenue=?, employees=?, founded_year=?, funding_total=?,
               education=?, philanthropy_focus=?, spouse=?, children=?, residence=?,
               updated_at=? WHERE id=?''',
            (data.get('name', ''), data.get('net_worth', 0), data.get('wealth_tier', 'millionaire'),
             data.get('email', ''), data.get('phone', ''), data.get('company', ''),
             data.get('title', ''), data.get('country', ''), data.get('state', ''),
             data.get('city', ''), data.get('industry', ''), data.get('source', ''),
             data.get('linkedin_url', ''), data.get('website_url', ''), data.get('notes', ''),
             data.get('tags', ''), data.get('status', 'new'),
             data.get('twitter_handle', ''), data.get('instagram_handle', ''),
             data.get('annual_revenue'), data.get('employees'), data.get('founded_year'),
             data.get('funding_total'), data.get('education', ''), data.get('philanthropy_focus', ''),
             data.get('spouse', ''), data.get('children'), data.get('residence', ''),
             datetime.now(), id)
        )
        conn.commit()
        conn.close()
        return jsonify({'updated': True})
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(contact) if contact else {})

@app.route('/api/contacts/bulk-update', methods=['POST'])
def bulk_update_contacts():
    data = request.json
    conn = get_db()
    updated = 0
    for c in data.get('contacts', []):
        conn.execute(
            '''UPDATE contacts SET email=?, phone=?, company=?, title=?, linkedin_url=?, website_url=?,
               notes=?, tags=?, status=?, updated_at=? WHERE id=?''',
            (c.get('email', ''), c.get('phone', ''), c.get('company', ''),
             c.get('title', ''), c.get('linkedin_url', ''), c.get('website_url', ''),
             c.get('notes', ''), c.get('tags', ''), c.get('status', 'new'), datetime.now(), c['id'])
        )
        updated += 1
    conn.commit()
    conn.close()
    return jsonify({'updated': updated})

@app.route('/api/contacts/delete', methods=['POST'])
def delete_contacts():
    data = request.json
    ids = data.get('ids', [])
    if ids:
        conn = get_db()
        conn.execute('DELETE FROM contacts WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
        conn.commit()
        conn.close()
    return jsonify({'deleted': len(ids)})

@app.route('/api/contacts/find-emails', methods=['POST'])
def api_find_emails():
    data = request.json
    contact_ids = data.get('contact_ids')
    limit = data.get('limit', 50)
    result = find_contact_info_batch(contact_ids=contact_ids, limit=limit)
    return jsonify({'found': result['emails'], 'phones': result['phones'], 'linkedin': result['linkedin']})

@app.route('/api/contacts/lookup-emails/<int:id>', methods=['POST'])
def api_lookup_contact_emails(id):
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not contact:
        return jsonify({'error': 'Not found'}), 404
    results = find_emails_for_contact(dict(contact))
    return jsonify({'results': results})

@app.route('/scrape')
def scrape_page():
    return render_template('scrape.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    data = request.json
    max_items = data.get('max_items', 500)
    count = run_scrape_all(max_items)
    return jsonify({'count': count})

@app.route('/api/scrape/<source>', methods=['POST'])
def api_scrape_source(source):
    data = request.json or {}
    max_items = data.get('max_items', 200)
    count = run_scrape_source(source, max_items)
    return jsonify({'count': count, 'source': source})

@app.route('/api/import', methods=['POST'])
def api_import():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))
        contacts = []
        skipped = 0
        for i, row in enumerate(reader, 1):
            name = (row.get('name') or row.get('Name') or row.get('full_name') or row.get('Full Name') or '').strip()
            if not name:
                skipped += 1
                continue
            net_str = (row.get('net_worth') or row.get('Net Worth') or row.get('NetWorth') or '0').replace('$','').replace(',','').strip()
            try:
                net_worth = float(net_str.replace('B','').replace('M',''))
                if 'M' in (row.get('net_worth') or row.get('Net Worth') or ''):
                    net_worth = net_worth / 1000
            except:
                net_worth = 0
            contacts.append({
                'rank': i, 'name': name, 'net_worth': net_worth,
                'source': row.get('source') or row.get('Source') or 'CSV Import',
                'industry': row.get('industry') or row.get('Industry') or '',
                'country': row.get('country') or row.get('Country') or '',
                'state': row.get('state') or row.get('State') or '',
                'city': row.get('city') or row.get('City') or '',
                'age': None,
                'company': row.get('company') or row.get('Company') or '',
                'email': row.get('email') or row.get('Email') or '',
                'phone': row.get('phone') or row.get('Phone') or '',
                'title': row.get('title') or row.get('Title') or '',
            })
        
        conn = get_db()
        inserted = 0
        for c in contacts:
            conn.execute(
                'INSERT INTO contacts (rank, name, net_worth, source, industry, country, state, city, company, email, phone, title, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (c['rank'], c['name'], c['net_worth'], c['source'], c['industry'],
                 c['country'], c['state'], c['city'], c['company'],
                 c.get('email', ''), c.get('phone', ''), c.get('title', ''), 'new')
            )
            inserted += 1
        conn.commit()
        conn.execute('INSERT INTO import_logs (filename, rows_imported, rows_skipped, source) VALUES (?,?,?,?)',
                    (file.filename, inserted, skipped, 'CSV Upload'))
        conn.commit()
        conn.close()
        return jsonify({'imported': inserted, 'skipped': skipped})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns')
def campaigns():
    conn = get_db()
    campaigns_list = conn.execute('SELECT * FROM campaigns ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('campaigns.html', campaigns=campaigns_list)

@app.route('/campaign/new', methods=['GET', 'POST'])
def new_campaign():
    if request.method == 'POST':
        conn = get_db()
        target = request.form.get('target_tier', 'all')
        target_count = 0
        if target and target != 'all':
            target_count = conn.execute('SELECT COUNT(*) FROM contacts WHERE wealth_tier = ? AND email IS NOT NULL AND email != ""', (target,)).fetchone()[0]
        else:
            target_count = conn.execute('SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ""').fetchone()[0]
        
        body = request.form['body']
        follow_ups_raw = request.form.get('follow_ups', '[]')
        try:
            follow_ups = json.loads(follow_ups_raw) if isinstance(follow_ups_raw, str) else follow_ups_raw
        except:
            follow_ups = []
        conn.execute(
            'INSERT INTO campaigns (name, subject, body, follow_ups, target_tier, target_count, status) VALUES (?,?,?,?,?,?,?)',
            (request.form['name'], request.form['subject'], body, json.dumps(follow_ups), target, target_count, 'draft')
        )
        conn.commit()
        conn.close()
        return redirect(url_for('campaigns'))
    conn = get_db()
    templates = conn.execute('SELECT * FROM templates').fetchall()
    conn.close()
    return render_template('campaign_form.html', templates=templates, campaign=None)

@app.route('/campaign/<int:id>')
def view_campaign(id):
    conn = get_db()
    campaign = dict(conn.execute('SELECT * FROM campaigns WHERE id = ?', (id,)).fetchone())
    try:
        campaign['follow_ups'] = json.loads(campaign.get('follow_ups', '[]'))
    except:
        campaign['follow_ups'] = []
    messages = conn.execute(
        'SELECT m.*, c.name as contact_name, c.net_worth, c.wealth_tier FROM messages m LEFT JOIN contacts c ON m.contact_id = c.id WHERE m.campaign_id = ? ORDER BY m.sent_at DESC',
        (id,)
    ).fetchall()
    stats = conn.execute(
        'SELECT COUNT(*) as total, SUM(CASE WHEN status="sent" THEN 1 ELSE 0 END) as sent, SUM(CASE WHEN replied_at IS NOT NULL THEN 1 ELSE 0 END) as replies, SUM(CASE WHEN donated_amount IS NOT NULL THEN 1 ELSE 0 END) as donations, COALESCE(SUM(donated_amount), 0) as donation_total FROM messages WHERE campaign_id = ?',
        (id,)
    ).fetchone()
    # Count replies per contact to track follow-up stage
    contact_stages = {}
    for m in messages:
        cid = m['contact_id']
        contact_stages[cid] = contact_stages.get(cid, 0) + 1
    conn.close()
    return render_template('campaign_view.html', campaign=campaign, messages=messages, stats=stats, contact_stages=contact_stages)

@app.route('/campaign/<int:id>/edit', methods=['GET', 'POST'])
def edit_campaign(id):
    conn = get_db()
    if request.method == 'POST':
        follow_ups_raw = request.form.get('follow_ups', '[]')
        try:
            follow_ups = json.loads(follow_ups_raw) if isinstance(follow_ups_raw, str) else follow_ups_raw
        except:
            follow_ups = []
        conn.execute(
            'UPDATE campaigns SET name=?, subject=?, body=?, follow_ups=? WHERE id=?',
            (request.form['name'], request.form['subject'], request.form['body'], json.dumps(follow_ups), id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('view_campaign', id=id))
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (id,)).fetchone()
    templates = conn.execute('SELECT * FROM templates').fetchall()
    conn.close()
    return render_template('campaign_form.html', campaign=campaign, templates=templates)

@app.route('/campaign/<int:id>/launch', methods=['POST'])
def launch_campaign(id):
    data = request.json or {}
    result = run_campaign(id, delay_min=data.get('delay_min', 10), delay_max=data.get('delay_max', 60))
    return jsonify(result)

@app.route('/campaign/<int:id>/send-followups', methods=['POST'])
def send_campaign_followups(id):
    data = request.json or {}
    from email_sender import send_follow_ups
    result = send_follow_ups(id, batch_size=data.get('batch_size', 50))
    return jsonify(result)

@app.route('/campaign/<int:id>/delete', methods=['POST'])
def delete_campaign(id):
    conn = get_db()
    conn.execute('DELETE FROM messages WHERE campaign_id = ?', (id,))
    conn.execute('DELETE FROM campaigns WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('campaigns'))

@app.route('/templates')
def templates():
    conn = get_db()
    templates_list = conn.execute('SELECT * FROM templates').fetchall()
    conn.close()
    return render_template('templates.html', templates=templates_list)

@app.route('/api/templates')
def api_templates():
    conn = get_db()
    templates_list = [dict(r) for r in conn.execute('SELECT * FROM templates').fetchall()]
    conn.close()
    return jsonify(templates_list)

@app.route('/api/templates', methods=['POST'])
def api_create_template():
    data = request.json
    conn = get_db()
    conn.execute(
        'INSERT INTO templates (name, subject, body, category) VALUES (?,?,?,?)',
        (data['name'], data['subject'], data['body'], data.get('category', 'general'))
    )
    conn.commit()
    template_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return jsonify({'id': template_id})

@app.route('/api/templates/<int:id>', methods=['DELETE'])
def api_delete_template(id):
    conn = get_db()
    conn.execute('DELETE FROM templates WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'deleted': True})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        conn = get_db()
        keys = ['smtp_server', 'smtp_port', 'smtp_email', 'smtp_password', 'smtp_use_tls',
                'sender_name', 'reply_to', 'daily_limit', 'delay_min', 'delay_max',
                'paypal_link', 'venmo_link', 'cashapp_link',
                'btc_address', 'eth_address', 'sol_address',
                'payment_note']
        for key in keys:
            value = request.form.get(key, '')
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)', (key, value))
        conn.commit()
        conn.close()
        return redirect(url_for('settings'))
    conn = get_db()
    current = {}
    for row in conn.execute('SELECT key, value FROM settings'):
        current[row['key']] = row['value']
    conn.close()
    return render_template('settings.html', settings=current)

@app.route('/api/settings')
def api_settings():
    return jsonify(get_settings())

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    billionaires = conn.execute("SELECT COUNT(*) FROM contacts WHERE wealth_tier='billionaire'").fetchone()[0]
    millionaires = conn.execute("SELECT COUNT(*) FROM contacts WHERE wealth_tier IN ('millionaire','multi-millionaire','centi-millionaire')").fetchone()[0]
    with_email = conn.execute('SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ""').fetchone()[0]
    sent = conn.execute('SELECT COUNT(*) FROM messages WHERE status="sent"').fetchone()[0]
    campaigns_count = conn.execute('SELECT COUNT(*) FROM campaigns').fetchone()[0]
    running = conn.execute('SELECT COUNT(*) FROM campaigns WHERE status="running"').fetchone()[0]
    donations = conn.execute('SELECT COALESCE(SUM(donated_amount), 0) FROM messages WHERE donated_amount IS NOT NULL').fetchone()[0]
    
    top = [dict(r) for r in conn.execute('SELECT name, net_worth, wealth_tier, country FROM contacts ORDER BY net_worth DESC LIMIT 10').fetchall()]
    by_country = [dict(r) for r in conn.execute('SELECT country, COUNT(*) as count FROM contacts WHERE country IS NOT NULL AND country != "" GROUP BY country ORDER BY count DESC LIMIT 15').fetchall()]
    by_tier = [dict(r) for r in conn.execute('SELECT wealth_tier, COUNT(*) as count FROM contacts GROUP BY wealth_tier ORDER BY count DESC').fetchall()]
    
    conn.close()
    return jsonify({
        'total': total, 'billionaires': billionaires, 'millionaires': millionaires,
        'with_email': with_email, 'sent': sent, 'campaigns': campaigns_count,
        'running': running, 'donations': donations,
        'top_10': top, 'by_country': by_country, 'by_tier': by_tier,
    })

@app.route('/api/countries')
def api_countries():
    conn = get_db()
    countries = [r['country'] for r in conn.execute('SELECT DISTINCT country FROM contacts WHERE country IS NOT NULL AND country != "" ORDER BY country').fetchall()]
    conn.close()
    return jsonify(countries)

@app.route('/api/export')
def api_export():
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY net_worth DESC').fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Name', 'Net Worth (B)', 'Wealth Tier', 'Email', 'Phone', 'Company', 'Title',
                     'Industry', 'Country', 'State', 'City', 'Source', 'LinkedIn', 'Website', 'Status', 'Notes',
                     'Twitter', 'Instagram', 'Annual Revenue', 'Employees', 'Founded', 'Funding',
                     'Education', 'Philanthropy Focus', 'Spouse', 'Children', 'Residence'])
    for c in contacts:
        writer.writerow([c['rank'], c['name'], c['net_worth'], c['wealth_tier'], c['email'], c['phone'],
                        c['company'], c['title'], c['industry'], c['country'], c['state'], c['city'],
                        c['source'], c['linkedin_url'], c['website_url'], c['status'], c['notes'],
                        c['twitter_handle'], c['instagram_handle'], c['annual_revenue'], c['employees'],
                        c['founded_year'], c['funding_total'], c['education'], c['philanthropy_focus'],
                        c['spouse'], c['children'], c['residence']])
    return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=wealthy_contacts.csv'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
