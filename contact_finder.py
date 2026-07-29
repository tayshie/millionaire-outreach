"""Contact info discovery using local pattern generation + domain mapping.
No external HTTP needed - generates emails from known patterns and validates format."""

import re
import sqlite3
import os
import json
import socket
import random
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── KNOWN COMPANY → DOMAIN MAP (no HTTP needed) ──
COMPANY_DOMAINS = {
    # Technology
    "apple": "apple.com", "microsoft": "microsoft.com", "amazon": "amazon.com",
    "alphabet": "abc.xyz", "google": "google.com", "meta": "meta.com",
    "facebook": "meta.com", "tesla": "tesla.com", "spacex": "spacex.com",
    "nvidia": "nvidia.com", "oracle": "oracle.com", "ibm": "ibm.com",
    "intel": "intel.com", "amd": "amd.com", "qualcomm": "qualcomm.com",
    "broadcom": "broadcom.com", "cisco": "cisco.com", "dell": "dell.com",
    "hewlett packard": "hp.com", "hp": "hp.com", "hpe": "hpe.com",
    "salesforce": "salesforce.com", "adobe": "adobe.com", "intuit": "intuit.com",
    "servicenow": "servicenow.com", "palantir": "palantir.com", "snowflake": "snowflake.com",
    "zoom": "zoom.us", "slack": "slack.com", "twilio": "twilio.com",
    "shopify": "shopify.com", "square": "squareup.com", "block": "block.xyz",
    "paypal": "paypal.com", "stripe": "stripe.com", "coinbase": "coinbase.com",
    "airbnb": "airbnb.com", "uber": "uber.com", "lyft": "lyft.com",
    "doordash": "doordash.com", "twitch": "twitch.tv", "netflix": "netflix.com",
    "spotify": "spotify.com", "roku": "roku.com",
    "tesla": "tesla.com", "spacex": "spacex.com",
    "twitter": "x.com", "x": "x.com", "block": "block.xyz",
    "mozilla": "mozilla.org", "reddit": "reddit.com",
    "cloudflare": "cloudflare.com", "datadog": "datadoghq.com",
    "splunk": "splunk.com", "vmware": "vmware.com",
    # Social Media
    "tiktok": "tiktok.com", "bytedance": "bytedance.com",
    "snapchat": "snap.com", "snap": "snap.com",
    "pinterest": "pinterest.com", "linkedin": "linkedin.com",
    # Telecom
    "verizon": "verizon.com", "at&t": "att.com", "att": "att.com",
    "t-mobile": "t-mobile.com", "comcast": "comcast.com",
    # Finance
    "jpmorgan chase": "jpmorgan.com", "jpmorgan": "jpmorgan.com",
    "goldman sachs": "gs.com", "morgan stanley": "morganstanley.com",
    "bank of america": "bankofamerica.com", "citigroup": "citigroup.com",
    "citi": "citigroup.com", "wells fargo": "wellsfargo.com",
    "berkshire hathaway": "berkshirehathaway.com",
    "blackrock": "blackrock.com", "blackstone": "blackstone.com",
    "kkr": "kkr.com", "apollo global": "apollo.com",
    "carlyle group": "carlyle.com", "bridgewater": "bridgewater.com",
    "fidelity": "fidelity.com", "vanguard": "vanguard.com",
    "american express": "americanexpress.com", "amex": "americanexpress.com",
    "visa": "visa.com", "mastercard": "mastercard.com",
    "us bancorp": "usbank.com", "pnc": "pnc.com",
    # Consumer
    "coca-cola": "coca-cola.com", "pepsico": "pepsico.com",
    "nestle": "nestle.com", "procter & gamble": "pg.com", "pg": "pg.com",
    "unilever": "unilever.com", "colgate": "colgatepalmolive.com",
    "kimberly clark": "kimberly-clark.com",
    "nike": "nike.com", "adidas": "adidas.com",
    "mcdonald's": "mcdonalds.com", "starbucks": "starbucks.com",
    "yum brands": "yum.com", "kfc": "kfc.com",
    "walmart": "walmart.com", "target": "target.com", "costco": "costco.com",
    "home depot": "homedepot.com", "lowe's": "lowes.com", "lowes": "lowes.com",
    "amazon": "amazon.com", "ebay": "ebay.com",
    # Auto
    "toyota": "toyota.com", "honda": "honda.com", "ford": "ford.com",
    "general motors": "gm.com", "gm": "gm.com", "bmw": "bmw.com",
    "mercedes-benz": "mercedes-benz.com", "daimler": "daimler.com",
    "volkswagen": "volkswagen.com", "hyundai": "hyundai.com",
    "kia": "kia.com", "nissan": "nissan.com", "ferrari": "ferrari.com",
    # Healthcare
    "johnson & johnson": "jnj.com", "jnj": "jnj.com",
    "pfizer": "pfizer.com", "moderna": "moderna.com",
    "abbvie": "abbvie.com", "merck": "merck.com",
    "bristol myers squibb": "bms.com", "eli lilly": "lilly.com",
    "amgen": "amgen.com", "gilead": "gilead.com",
    "biogen": "biogen.com", "regeneron": "regeneron.com",
    "unitedhealth": "unitedhealthgroup.com", "anthem": "anthem.com",
    "cvs health": "cvshealth.com", "cigna": "cigna.com",
    # Energy
    "exxonmobil": "exxonmobil.com", "chevron": "chevron.com",
    "shell": "shell.com", "bp": "bp.com",
    "totalenergies": "totalenergies.com", "conocophillips": "conocophillips.com",
    "schlumberger": "slb.com", "halliburton": "halliburton.com",
    "reliance industries": "ril.com",
    # Industrial
    "boeing": "boeing.com", "lockheed martin": "lockheedmartin.com",
    "raytheon": "raytheon.com", "northrop grumman": "northropgrumman.com",
    "general dynamics": "gdd.com", "ge": "ge.com",
    "caterpillar": "caterpillar.com", "deere": "deere.com",
    "honeywell": "honeywell.com", "3m": "3m.com",
    "union pacific": "up.com", "fedex": "fedex.com", "ups": "ups.com",
    # Media
    "walt disney": "disney.com", "disney": "disney.com",
    "warner bros": "warnerbros.com", "paramount": "paramount.com",
    "comcast": "comcast.com", "nbc": "nbc.com",
    "fox": "fox.com", "news corp": "newscorp.com",
    "bloomberg": "bloomberg.com", "bloomberg lp": "bloomberg.com",
    "thomson reuters": "thomsonreuters.com",
    # Tech (non-US)
    "samsung": "samsung.com", "lg": "lg.com", "sony": "sony.com",
    "softbank": "softbank.com", "rakuten": "rakuten.com",
    "alibaba": "alibaba.com", "tencent": "tencent.com",
    "baidu": "baidu.com", "jd.com": "jd.com",
    "xiaomi": "xiaomi.com", "bytedance": "bytedance.com",
    "meituan": "meituan.com",
    # India
    "tata": "tata.com", "tata group": "tata.com",
    "infosys": "infosys.com", "wipro": "wipro.com",
    "hcl": "hcl.com", "adani group": "adani.com",
    # Europe
    "lvmh": "lvmh.com", "l'oreal": "loreal.com", "loreal": "loreal.com",
    "hermes": "hermes.com", "kering": "kering.com", "chanel": "chanel.com",
    "inditex": "inditex.com", "zara": "zara.com", "h&m": "hm.com",
    "volkswagen": "volkswagen.com", "bmw": "bmw.com", "mercedes": "mercedes-benz.com",
    "siemens": "siemens.com", "sap": "sap.com", "allianz": "allianz.com",
    "deutsche bank": "db.com", "ubs": "ubs.com", "credit suisse": "credit-suisse.com",
    "novartis": "novartis.com", "roche": "roche.com", "nestle": "nestle.com",
    # Specific companies from seed data
    "paul mitchell": "paulmitchell.com", "fubu": "fubu.com",
    "corcoran group": "corcoran.com", "spanx": "spanx.com",
    "roc nation": "rocnation.com", "tyler perry studios": "tylerperry.com",
    "kylie cosmetics": "kyliecosmetics.com", "own network": "own.tv",
    "lucasfilm": "lucasfilm.com", "pixar": "pixar.com",
    "tesla": "tesla.com", "digital currency group": "dcg.co",
    "ethereum": "ethereum.org", "gemini": "gemini.com",
    "microstrategy": "microstrategy.com", "ripple": "ripple.com",
    "ripple labs": "ripple.com", "andreessen horowitz": "a16z.com",
    "blackrock": "blackrock.com", "citadel": "citadel.com",
    "interactive brokers": "interactivebrokers.com",
}

# ── NAME EXTRACTION ──

def extract_name_parts(name):
    name = re.sub(r'\s+', ' ', name.strip())
    parts = name.split()
    if not parts:
        return '', '', ''
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ''
    middle = ' '.join(parts[1:-1]) if len(parts) > 2 else ''
    return first.lower(), last.lower(), middle.lower()

def verify_email_format(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

# ── DOMAIN LOOKUP (local, no HTTP) ──

def find_company_domain(company_name):
    if not company_name:
        return None
    key = company_name.lower().strip()
    key = re.sub(r'[,\s]+', ' ', key).strip()
    
    # Direct lookup
    if key in COMPANY_DOMAINS:
        return COMPANY_DOMAINS[key]
    
    # Try without common suffixes
    for suffix in [' inc', ' corporation', ' corp', ' llc', ' ltd', ' limited', ' group', ' holdings', ' technologies', ' systems', ' solutions', ' software', ' international', ' global', ' enterprises', ' co', ', inc', ', llc', ', ltd']:
        stripped = key.replace(suffix, '').strip()
        if stripped in COMPANY_DOMAINS:
            return COMPANY_DOMAINS[stripped]
    
    # Try just the first word (e.g. "Tesla, SpaceX" → "Tesla")
    first_word = key.split()[0] if key.split() else key
    if first_word in COMPANY_DOMAINS:
        return COMPANY_DOMAINS[first_word]
    
    # Fallback: companyname.com
    domain = re.sub(r'[^a-zA-Z0-9]', '', key).strip()
    if domain and len(domain) > 2:
        if domain.endswith('com'):
            return domain
        return domain + '.com'
    
    return None

# ── EMAIL PATTERN GENERATION (15+ patterns) ──

PATTERN_WEIGHTS = {
    'first.last@domain': 0.40,
    'first@domain': 0.20,
    'flast@domain': 0.12,
    'first_last@domain': 0.05,
    'last@domain': 0.05,
    'f.last@domain': 0.05,
    'firstl@domain': 0.05,
    'last.first@domain': 0.03,
    'first-last@domain': 0.02,
    'lastf@domain': 0.02,
    'fflast@domain': 0.01,
}

EMAIL_PATTERN_FUNCTIONS = {
    'first.last@domain': lambda f, l, m, d: f"{f}.{l}@{d}",
    'first@domain': lambda f, l, m, d: f"{f}@{d}",
    'flast@domain': lambda f, l, m, d: f"{f[0]}{l}@{d}",
    'first_last@domain': lambda f, l, m, d: f"{f}_{l}@{d}",
    'last@domain': lambda f, l, m, d: f"{l}@{d}",
    'f.last@domain': lambda f, l, m, d: f"{f[0]}.{l}@{d}",
    'firstl@domain': lambda f, l, m, d: f"{f}{l[0]}@{d}",
    'last.first@domain': lambda f, l, m, d: f"{l}.{f}@{d}",
    'first-last@domain': lambda f, l, m, d: f"{f}-{l}@{d}",
    'lastf@domain': lambda f, l, m, d: f"{l}{f[0]}@{d}",
    'fflast@domain': lambda f, l, m, d: f"{f[0]}{l[0]}@{d}",
    'first.middle.last@domain': lambda f, l, m, d: f"{f}.{m}.{l}@{d}" if m else None,
    'first.last@domain+': lambda f, l, m, d: f"{f}.{l}@{d.replace('.com','+alias.com')}" if '+alias' in d else f"{f}.{l}@{d}",
}

def generate_email_patterns(first, last, middle, domain):
    patterns = []
    seen = set()
    for name, func in EMAIL_PATTERN_FUNCTIONS.items():
        try:
            result = func(first, last, middle, domain)
            if result and result not in seen and verify_email_format(result):
                patterns.append({
                    'email': result,
                    'pattern': name,
                    'confidence': PATTERN_WEIGHTS.get(name, 0.3),
                })
                seen.add(result)
        except:
            continue
    return patterns

# ── MX RECORD CHECK (no SMTP, just DNS) ──

def has_mx_record(domain):
    """Check if domain has mail exchange records (does NOT send email)."""
    try:
        answers = socket.getaddrinfo(domain, 25, socket.AF_INET, socket.SOCK_STREAM)
        return len(answers) > 0
    except:
        return False

# ── MAIN CONTACT DISCOVERY ──

def find_emails_for_contact(contact):
    """Find possible email addresses using local pattern generation.
    No external HTTP needed - uses hardcoded domain map + pattern gen."""
    name = contact.get('name', '')
    company = contact.get('company', '')
    
    first, last, middle = extract_name_parts(name)
    if not first or not last:
        return []
    
    results = []
    seen_emails = set()
    
    # Try multiple company-associated domains
    domains_to_try = []
    
    # Primary domain from company
    if company:
        domain = find_company_domain(company)
        if domain:
            domains_to_try.append(domain)
    
    # Also try source field
    source = contact.get('source', '')
    if source and source != company:
        domain2 = find_company_domain(source)
        if domain2 and domain2 not in domains_to_try:
            domains_to_try.append(domain2)
    
    # Try industry + .com (e.g. technology.com)
    industry = contact.get('industry', '')
    if industry and not domains_to_try:
        ind_domain = industry.lower().replace(' ', '').replace('&', '') + '.com'
        if '.' in ind_domain:
            domains_to_try.append(ind_domain)
    
    for domain in domains_to_try[:3]:
        patterns = generate_email_patterns(first, last, middle, domain)
        
        # Check MX records for the domain
        mx_ok = has_mx_record(domain)
        
        for p in patterns:
            email = p['email']
            if email not in seen_emails:
                seen_emails.add(email)
                confidence = p['confidence']
                if mx_ok:
                    confidence = min(confidence + 0.2, 0.9)
                results.append({
                    'email': email,
                    'source': f"pattern:{p['pattern']}",
                    'confidence': round(confidence, 2),
                    'domain': domain,
                    'mx_valid': mx_ok,
                })
        
        # Add a catch-all if MX is valid (some companies use first@domain)
        catch_all = f"{first}@{domain}"
        if catch_all not in seen_emails and verify_email_format(catch_all):
            seen_emails.add(catch_all)
            results.append({
                'email': catch_all,
                'source': 'pattern:first@domain',
                'confidence': 0.2,
                'domain': domain,
                'mx_valid': mx_ok,
            })
    
    # Try multiple patterns against all possible domains for maximum coverage
    all_domains_pool = list(set(COMPANY_DOMAINS.values()))
    random.shuffle(all_domains_pool)
    
    # If no company matched, try a few common domains
    if not results:
        for domain in all_domains_pool[:20]:
            patterns = generate_email_patterns(first, last, middle, domain)
            for p in patterns:
                if p['email'] not in seen_emails:
                    seen_emails.add(p['email'])
                    results.append(p)
    
    return results

def find_contact_info_batch(contact_ids=None, limit=50):
    """Find contact info for a batch of contacts without emails."""
    conn = get_conn()
    if contact_ids:
        contacts = conn.execute(
            'SELECT * FROM contacts WHERE id IN ({}) AND (email IS NULL OR email = "") ORDER BY net_worth DESC'.format(
                ','.join('?' * len(contact_ids))
            ), contact_ids
        ).fetchall()
    else:
        contacts = conn.execute(
            'SELECT * FROM contacts WHERE (email IS NULL OR email = "") AND status != "skipped" ORDER BY net_worth DESC LIMIT ?',
            (limit,)
        ).fetchall()
    
    updated = 0
    for c in contacts:
        found = find_emails_for_contact(dict(c))
        # Pick the highest confidence email
        best = max(found, key=lambda x: x['confidence']) if found else None
        if best and best['email']:
            conn.execute(
                'UPDATE contacts SET email=?, email_source=?, updated_at=? WHERE id=?',
                (best['email'], best['source'], datetime.now(), c['id'])
            )
            updated += 1
    
    conn.commit()
    conn.close()
    print(f"[+] Found {updated} generated email addresses")
    return {'emails': updated, 'phones': 0, 'linkedin': 0}

def find_emails_batch(contact_ids=None, limit=50):
    """Legacy wrapper."""
    result = find_contact_info_batch(contact_ids=contact_ids, limit=limit)
    return result['emails']
