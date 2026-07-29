import requests
import sqlite3
import os
import re
import csv
import io
import time
import random
import concurrent.futures
from urllib.parse import urlparse, urljoin
from datetime import datetime
from bs4 import BeautifulSoup

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def ua():
    return random.choice(USER_AGENTS)

# ── SOURCE 1: FORBES ──

def scrape_forbes_billionaires(max_items=500):
    print(f"[*] Forbes billionaires...")
    results = []
    urls = [
        'https://www.forbes.com/forbesapi/org/forbesapi/position/true/position/1.json',
        'https://www.forbes.com/ajax/list/data?type=person&year=0&uri=rtb',
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers={'User-Agent': ua(), 'Accept': 'application/json'}, timeout=30)
            data = resp.json()
            items = data.get('positionList', {}).get('positionItems', []) or data.get('listItems', []) or data if isinstance(data, list) else []
            for i, item in enumerate(items[:max_items], 1):
                if isinstance(item, dict):
                    name = (item.get('personName') or item.get('name') or '').replace('&#039;', "'")
                    nw = float(item.get('worth', item.get('netWorth', 0)) or 0)
                    results.append({
                        'rank': i, 'name': name, 'net_worth': nw, 'wealth_tier': 'billionaire',
                        'source': item.get('source', '') or item.get('industry', ''),
                        'industry': item.get('category', item.get('industry', '')),
                        'country': item.get('country', item.get('citizenship', '')),
                        'state': item.get('state', ''), 'city': item.get('city', ''),
                        'age': item.get('age'), 'company': item.get('organizationName', ''),
                    })
            if results:
                break
        except:
            continue
    print(f"  → {len(results)} billionaires")
    return results

# ── SOURCE 2: WIKIPEDIA CATEGORIES ──

def scrape_wikipedia_wealthy(max_items=300):
    print(f"[*] Wikipedia wealthy categories...")
    results = []
    categories = [
        'Category:American_billionaires',
        'Category:Billionaires_by_country',
        'Category:American_chief_executives',
        'Category:American_tech_entrepreneurs',
        'Category:American_philanthropists',
        'Category:Hedge_fund_managers',
        'Category:American_real_estate_entrepreneurs',
    ]
    for cat in categories[:4]:
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/w/api.php",
                params={'action': 'query', 'list': 'categorymembers',
                        'cmtitle': cat, 'format': 'json', 'cmlimit': 'max'},
                headers={'User-Agent': 'OutreachApp/1.0'}, timeout=15
            )
            data = resp.json()
            for member in data.get('query', {}).get('categorymembers', [])[:max_items//len(categories)]:
                title = member.get('title', '').replace('_', ' ')
                if ':' in title or '/' in title or len(title) < 5:
                    continue
                if not any(r['name'] == title for r in results):
                    results.append({
                        'rank': len(results)+1, 'name': title, 'net_worth': 0,
                        'wealth_tier': 'millionaire', 'source': f'Wikipedia:{cat.split(":")[-1]}',
                        'industry': '', 'country': '', 'state': '', 'city': '',
                        'age': None, 'company': '',
                    })
        except:
            continue
    print(f"  → {len(results)} from Wikipedia")
    return results

# ── SOURCE 3: SEC EDGAR INSIDER FILINGS ──

def scrape_sec_edgar_insiders(max_items=200):
    print(f"[*] SEC EDGAR insider filings (has contact info)...")
    results = []
    try:
        resp = requests.get(
            'https://efts.sec.gov/LATEST/search-index',
            params={'q': 'formType:(4 OR 3) AND transactionAmount:>5000000',
                    'dateRange': '1m', 'page': 1, 'size': max_items},
            headers={'User-Agent': 'OutreachApp/1.0 (research)', 'Accept': 'application/json'},
            timeout=20
        )
        data = resp.json()
        for hit in data.get('hits', {}).get('hits', []):
            src = hit.get('_source', {})
            owner = src.get('reportingOwner', {})
            name = owner.get('name', '')
            if not name:
                continue
            addr = owner.get('address', {})
            phone = owner.get('phoneNumber', '')
            company = src.get('issuerName', src.get('companyName', ''))
            ticker = src.get('issuerTradingSymbol', '')
            
            contact = {
                'rank': len(results)+1, 'name': name, 'net_worth': 0,
                'wealth_tier': 'millionaire', 'source': f'SEC Insider ({ticker}, {src.get("formType","")})',
                'industry': 'Finance/Public Company', 'country': 'United States',
                'state': addr.get('stateOrCountry', ''), 'city': addr.get('city', ''),
                'age': None, 'company': company,
            }
            
            if phone:
                contact['phone'] = phone
            if addr.get('street1'):
                contact['city'] = addr.get('city', '') or contact['city']
                contact['state'] = addr.get('stateOrCountry', '') or contact['state']
            
            results.append(contact)
        print(f"  → {len(results)} insider contacts")
    except Exception as e:
        print(f"  → SEC failed: {e}")
    return results

# ── SOURCE 4: COMPANY TEAM PAGES ──

def scrape_company_team_pages(max_items=200):
    print(f"[*] Company team page scraping (contact info rich)...")
    results = []
    conn = get_conn()
    contacts_no_email = conn.execute(
        'SELECT DISTINCT company FROM contacts WHERE company IS NOT NULL AND company != "" AND (email IS NULL OR email = "") AND status != "skipped" ORDER BY net_worth DESC LIMIT 50'
    ).fetchall()
    conn.close()
    
    for row in contacts_no_email:
        company = row['company']
        domain = _find_domain(company)
        if not domain:
            continue
        
        team_urls = [
            f"https://{domain}/team", f"https://{domain}/about", f"https://{domain}/about/team",
            f"https://{domain}/leadership", f"https://{domain}/about/leadership",
            f"https://{domain}/management", f"https://{domain}/company/team",
            f"https://www.{domain}/team", f"https://www.{domain}/about",
        ]
        
        for url in team_urls:
            try:
                resp = requests.get(url, timeout=8, headers={'User-Agent': ua()})
                soup = BeautifulSoup(resp.text, 'lxml')
                text = resp.text
                
                emails = set(re.findall(EMAIL_PATTERN, text.lower()))
                emails = {e for e in emails if not any(s in e for s in ['example.com', 'noreply@', 'info@', 'support@', 'admin@', 'webmaster@', 'contact@', 'sales@', 'marketing@', 'careers@'])}
                
                names_on_page = set()
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'span']):
                    t = tag.get_text(strip=True)
                    if t and len(t.split()) >= 2 and len(t.split()) <= 4:
                        names_on_page.add(t)
                
                for name in names_on_page:
                    name_parts = name.split()
                    if len(name_parts) >= 2:
                        results.append({
                            'rank': len(results)+1, 'name': name,
                            'net_worth': 0, 'wealth_tier': 'millionaire',
                            'source': f'Team page: {company}', 'industry': '',
                            'country': '', 'state': '', 'city': '',
                            'age': None, 'company': company,
                            '_email_hint': list(emails)[0] if emails else '',
                        })
                        if len(results) >= max_items:
                            return results
                
                if emails and len(results) < max_items:
                    for email in list(emails)[:5]:
                        name_from_email = email.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
                        if name_from_email and len(name_from_email) > 3:
                            results.append({
                                'rank': len(results)+1, 'name': name_from_email,
                                'net_worth': 0, 'wealth_tier': 'millionaire',
                                'source': f'Email scraped: {company}', 'industry': '',
                                'country': '', 'state': '', 'city': '',
                                'age': None, 'company': company, 'email': email,
                            })
                            if len(results) >= max_items:
                                return results
                
                if results:
                    break
            except:
                continue
        
        time.sleep(0.3)
    
    print(f"  → {len(results)} from team pages")
    return results

# ── SOURCE 5: ANGELIST / WELLFOUND ──

def scrape_angellist_wealthy(max_items=100):
    print(f"[*] AngelList/Wellfound investors...")
    results = []
    try:
        resp = requests.get(
            'https://api.angel.co/1/tags/1664/startups',  # Y Combinator tag
            headers={'User-Agent': ua(), 'Accept': 'application/json'},
            timeout=15
        )
    except:
        pass
    
    try:
        resp = requests.get(
            'https://www.angellist.com/collections/investors',
            headers={'User-Agent': ua()}, timeout=15
        )
        soup = BeautifulSoup(resp.text, 'lxml')
        for link in soup.select('a[href*="/profile/"]'):
            text = link.get_text(strip=True)
            if text and len(text.split()) >= 2:
                if text not in [r['name'] for r in results]:
                    results.append({
                        'rank': len(results)+1, 'name': text, 'net_worth': 0,
                        'wealth_tier': 'millionaire', 'source': 'AngelList',
                        'industry': 'Venture Capital', 'country': 'United States',
                        'state': '', 'city': '', 'age': None, 'company': '',
                    })
                    if len(results) >= max_items:
                        break
    except:
        pass
    
    print(f"  → {len(results)} from AngelList")
    return results

# ── SOURCE 6: GOOGLE DORKING FOR WEALTHY ──

def scrape_google_dork_wealthy(max_items=100):
    print(f"[*] Google dorking for wealthy contacts...")
    results = []
    seen = set()
    dork_queries = [
        'site:forbes.com billionaire CEO email',
        'site:bloomberg.com billionaire report',
        'site:businessinsider.com wealthy CEO',
        'site:forbes.com profile net worth',
        '"Chief Executive Officer" "net worth"',
        '"founder and CEO" billion',
    ]
    
    for query in dork_queries:
        try:
            resp = requests.get(
                f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en&num=20",
                headers={'User-Agent': ua()}, timeout=10
            )
            soup = BeautifulSoup(resp.text, 'lxml')
            for link in soup.select('a[href^="http"]'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                names = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
                for name in names:
                    if name not in seen and len(name) > 4:
                        seen.add(name)
                        results.append({
                            'rank': len(results)+1, 'name': name, 'net_worth': 0,
                            'wealth_tier': 'millionaire', 'source': f'Google:{query[:30]}',
                            'industry': '', 'country': '', 'state': '', 'city': '',
                            'age': None, 'company': '',
                        })
                        if len(results) >= max_items:
                            return results
        except:
            continue
    
    print(f"  → {len(results)} from Google dorking")
    return results

# ── SOURCE 7: BLOOMBERG PUBLIC PROFILES ──

def scrape_bloomberg_profiles(max_items=100):
    print(f"[*] Bloomberg executive profiles...")
    results = []
    try:
        resp = requests.get(
            'https://www.bloomberg.com/billionaires/',
            headers={'User-Agent': ua()}, timeout=15
        )
        soup = BeautifulSoup(resp.text, 'lxml')
        for tag in soup.select('[class*="name"], [class*="Name"], h2, h3'):
            text = tag.get_text(strip=True)
            if text and len(text.split()) >= 2 and len(text) < 50:
                if not any(r['name'] == text for r in results):
                    results.append({
                        'rank': len(results)+1, 'name': text, 'net_worth': 0,
                        'wealth_tier': 'billionaire', 'source': 'Bloomberg',
                        'industry': '', 'country': '', 'state': '', 'city': '',
                        'age': None, 'company': '',
                    })
                    if len(results) >= max_items:
                        break
    except:
        pass
    print(f"  → {len(results)} from Bloomberg")
    return results

# ── SOURCE 8: OPEN CORPORATES ──

def scrape_opencorporates_directors(max_items=100):
    print(f"[*] OpenCorporates director search...")
    results = []
    jurisdictions = ['us_de', 'us_ca', 'us_ny', 'us_tx', 'us_fl', 'gb', 'ie']
    for jur in [jurisdictions[0]]:
        try:
            resp = requests.get(
                f'https://api.opencorporates.com/v0.4/companies/search',
                params={'q': 'Inc.', 'jurisdiction_code': jur, 'per_page': 30},
                headers={'User-Agent': ua()}, timeout=15
            )
            data = resp.json()
            for company in data.get('results', [])[:20]:
                company_data = company.get('company', {})
                name = company_data.get('name', '')
                if not name:
                    continue
                officers_url = company.get('url', '') + '/officers'
                try:
                    resp2 = requests.get(
                        f"https://api.opencorporates.com/v0.4/companies/{jur}/{company_data.get('company_number', '')}/officers",
                        headers={'User-Agent': ua()}, timeout=10
                    )
                    off_data = resp2.json()
                    for officer in off_data.get('results', [])[:5]:
                        off = officer.get('officer', {})
                        off_name = off.get('name', '')
                        if off_name and off_name not in [r['name'] for r in results]:
                            results.append({
                                'rank': len(results)+1, 'name': off_name,
                                'net_worth': 0, 'wealth_tier': 'millionaire',
                                'source': f'OpenCorporates: {name}', 'industry': '',
                                'country': 'United States', 'state': jur.split('_')[-1].upper() if '_' in jur else jur.upper(),
                                'city': '', 'age': None, 'company': name,
                            })
                            if len(results) >= max_items:
                                return results
                except:
                    continue
        except:
            continue
    print(f"  → {len(results)} from OpenCorporates")
    return results

# ── SOURCE 9: NEWS + EMAIL DISCOVERY ──

def scrape_news_wealthy(max_items=150):
    print(f"[*] News source wealth extraction...")
    results = []
    seen_names = set()
    queries = [
        "billionaire 2025 CEO founder",
        "millionaire entrepreneur 2025",
        "tech founder net worth 2025",
        "hedge fund billionaire 2025",
        "real estate mogul 2025",
        "venture capital billionaire 2025",
    ]
    for query in queries[:4]:
        try:
            resp = requests.get(
                f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=en-US&gl=US",
                headers={'User-Agent': ua()}, timeout=10
            )
            soup = BeautifulSoup(resp.text, 'lxml')
            text = soup.get_text()
            
            matches = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)', text)
            for name in matches:
                name = name.strip()
                if name not in seen_names and len(name) > 4 and name.count(' ') <= 2:
                    seen_names.add(name)
                    results.append({
                        'rank': len(results)+1, 'name': name, 'net_worth': 0,
                        'wealth_tier': 'millionaire', 'source': f'News:{query[:20]}',
                        'industry': '', 'country': '', 'state': '', 'city': '',
                        'age': None, 'company': '',
                    })
                    if len(results) >= max_items:
                        return results
        except:
            continue
    print(f"  → {len(results)} from news")
    return results

# ── SOURCE 10: HUNUN ──

def scrape_hurun_rich_list(max_items=200):
    print(f"[*] Hurun Global Rich List...")
    results = []
    try:
        resp = requests.get(
            'https://www.hurun.net/en-US/Rank/Hs/GlobalRichList',
            headers={'User-Agent': ua()}, timeout=30
        )
        soup = BeautifulSoup(resp.text, 'lxml')
        for table in soup.find_all('table'):
            rows = table.find_all('tr')[1:max_items+1]
            for i, row in enumerate(rows, 1):
                cols = row.find_all('td')
                if len(cols) >= 3:
                    name = cols[1].get_text(strip=True)
                    if name and not any(r['name'] == name for r in results):
                        results.append({
                            'rank': i, 'name': name, 'net_worth': 0,
                            'wealth_tier': 'billionaire',
                            'source': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'industry': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            'country': cols[4].get_text(strip=True) if len(cols) > 4 else '',
                            'state': '', 'city': '', 'age': None, 'company': '',
                        })
    except:
        pass
    print(f"  → {len(results)} from Hurun")
    return results

# ── HELPERS ──

def _find_domain(company):
    try:
        resp = requests.get(
            'https://autocomplete.clearbit.com/v1/companies/suggest',
            params={'query': company}, timeout=5
        )
        if resp.status_code == 200:
            suggestions = resp.json()
            if suggestions:
                return suggestions[0].get('domain', '')
    except:
        pass
    domain = re.sub(r'[^a-zA-Z0-9]', '', company.lower()).strip() + '.com'
    return domain

def detect_wealth_tier(net_worth):
    if net_worth >= 1: return 'billionaire'
    elif net_worth >= 0.1: return 'centi-millionaire'
    elif net_worth >= 0.01: return 'multi-millionaire'
    elif net_worth > 0: return 'millionaire'
    return 'unknown'

def save_contacts(contacts, replace=False):
    conn = get_conn()
    if replace:
        conn.execute('DELETE FROM contacts')
    inserted = 0
    updated = 0
    for c in contacts:
        name = c.get('name', '').strip()
        if not name or len(name) < 2:
            continue
        tier = c.get('wealth_tier') or detect_wealth_tier(c.get('net_worth', 0))
        
        existing = conn.execute(
            'SELECT id, email FROM contacts WHERE name = ?',
            (name,)
        ).fetchone()
        
        has_email = c.get('email', '') or ''
        
        if existing:
            update_fields = ['net_worth=?, wealth_tier=?, source=?, industry=?, age=?, company=?, updated_at=?']
            update_params = [c.get('net_worth', 0), tier, c.get('source', ''), c.get('industry', ''),
                           c.get('age'), c.get('company', ''), datetime.now()]
            
            if has_email and not existing['email']:
                update_fields.append('email=?')
                update_params.append(has_email)
            if c.get('phone') and not conn.execute('SELECT phone FROM contacts WHERE id=?', (existing['id'],)).fetchone()['phone']:
                update_fields.append('phone=?')
                update_params.append(c['phone'])
            
            update_params.append(existing['id'])
            conn.execute(
                f'UPDATE contacts SET {", ".join(update_fields)} WHERE id=?',
                update_params
            )
            updated += 1
        else:
            conn.execute(
                '''INSERT INTO contacts (rank, name, net_worth, wealth_tier, source, industry, country, state, city, age, company, email, phone)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (c.get('rank', 0), name, c.get('net_worth', 0), tier,
                 c.get('source', ''), c.get('industry', ''), c.get('country', ''),
                 c.get('state', ''), c.get('city', ''), c.get('age'), c.get('company', ''),
                 has_email, c.get('phone', ''))
            )
            inserted += 1
    
    conn.commit()
    conn.close()
    print(f"[+] Saved {inserted} new, updated {updated} existing ({len(contacts)} processed)")
    return inserted

# ── RUN ALL ──

def run_scrape_all(max_items=500):
    """Run all scrapers in parallel for maximum coverage."""
    all_contacts = []
    
    sources = [
        scrape_forbes_billionaires,
        scrape_wikipedia_wealthy,
        scrape_sec_edgar_insiders,
        scrape_company_team_pages,
        scrape_news_wealthy,
        scrape_google_dork_wealthy,
        scrape_bloomberg_profiles,
        scrape_hurun_rich_list,
    ]
    
    # Run sources sequentially (to avoid IP blocks), but collect all
    for source_fn in sources:
        try:
            contacts = source_fn(max_items // len(sources) + 50)
            all_contacts.extend(contacts)
        except Exception as e:
            print(f"  ✗ {source_fn.__name__}: {e}")
    
    conn = get_conn()
    existing_count = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    conn.close()
    
    replace = existing_count <= 20
    count = save_contacts(all_contacts, replace=replace)
    return count

def run_scrape_source(source_name, max_items=200):
    """Run a single source by name."""
    sources = {
        'forbes': scrape_forbes_billionaires,
        'wikipedia': scrape_wikipedia_wealthy,
        'sec': scrape_sec_edgar_insiders,
        'teams': scrape_company_team_pages,
        'news': scrape_news_wealthy,
        'google': scrape_google_dork_wealthy,
        'bloomberg': scrape_bloomberg_profiles,
        'hurun': scrape_hurun_rich_list,
        'angellist': scrape_angellist_wealthy,
        'opencorporates': scrape_opencorporates_directors,
    }
    fn = sources.get(source_name)
    if not fn:
        return 0
    contacts = fn(max_items)
    return save_contacts(contacts)

def import_csv_data(filepath):
    results = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            name = row.get('name', row.get('Name', row.get('full_name', row.get('Full Name', ''))))
            if not name:
                continue
            net_worth_str = row.get('net_worth', row.get('Net Worth', row.get('NetWorth', '0'))).replace('$', '').replace('B', '').replace('M', '').replace(',', '').strip()
            try:
                net_worth = float(net_worth_str)
                if row.get('Net Worth', '').strip().endswith('M') or row.get('net_worth', '').strip().endswith('M'):
                    net_worth = net_worth / 1000
            except:
                net_worth = 0
            results.append({
                'rank': i, 'name': name.strip(), 'net_worth': net_worth,
                'source': row.get('source', row.get('Source', 'CSV Import')),
                'industry': row.get('industry', row.get('Industry', '')),
                'country': row.get('country', row.get('Country', '')),
                'state': row.get('state', row.get('State', '')),
                'city': row.get('city', row.get('City', '')),
                'age': None, 'company': row.get('company', row.get('Company', '')),
                'email': row.get('email', row.get('Email', '')),
                'phone': row.get('phone', row.get('Phone', '')),
                'title': row.get('title', row.get('Title', '')),
            })
    return results
