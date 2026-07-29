"""Efficient bulk email generator - runs in under 10 seconds."""
import sqlite3
import re

DB_PATH = __file__.replace('bulk_emails.py', 'outreach.db')

COMPANY_DOMAINS = {
    "apple": "apple.com", "microsoft": "microsoft.com", "amazon": "amazon.com",
    "google": "google.com", "alphabet": "abc.xyz", "meta": "meta.com",
    "facebook": "meta.com", "tesla": "tesla.com", "spacex": "spacex.com",
    "nvidia": "nvidia.com", "oracle": "oracle.com", "ibm": "ibm.com",
    "intel": "intel.com", "amd": "amd.com", "qualcomm": "qualcomm.com",
    "cisco": "cisco.com", "dell": "dell.com", "hp": "hp.com",
    "salesforce": "salesforce.com", "adobe": "adobe.com", "intuit": "intuit.com",
    "zoom": "zoom.us", "shopify": "shopify.com", "square": "squareup.com",
    "paypal": "paypal.com", "stripe": "stripe.com", "coinbase": "coinbase.com",
    "airbnb": "airbnb.com", "uber": "uber.com", "netflix": "netflix.com",
    "spotify": "spotify.com", "twitter": "x.com",
    "jpmorgan": "jpmorgan.com", "goldman sachs": "gs.com",
    "morgan stanley": "morganstanley.com", "bank of america": "bankofamerica.com",
    "citigroup": "citigroup.com", "wells fargo": "wellsfargo.com",
    "berkshire hathaway": "berkshirehathaway.com",
    "blackrock": "blackrock.com", "blackstone": "blackstone.com",
    "kkr": "kkr.com", "apollo global": "apollo.com",
    "coca-cola": "coca-cola.com", "pepsico": "pepsico.com",
    "nestle": "nestle.com", "pg": "pg.com", "procter & gamble": "pg.com",
    "unilever": "unilever.com", "nike": "nike.com", "adidas": "adidas.com",
    "mcdonald's": "mcdonalds.com", "starbucks": "starbucks.com",
    "walmart": "walmart.com", "target": "target.com", "costco": "costco.com",
    "home depot": "homedepot.com", "lowes": "lowes.com",  "lowe's": "lowes.com",
    "ebay": "ebay.com",
    "toyota": "toyota.com", "honda": "honda.com", "ford": "ford.com",
    "general motors": "gm.com", "bmw": "bmw.com", "mercedes-benz": "mercedes-benz.com",
    "volkswagen": "volkswagen.com", "hyundai": "hyundai.com", "ferrari": "ferrari.com",
    "jnj": "jnj.com", "johnson & johnson": "jnj.com",
    "pfizer": "pfizer.com", "moderna": "moderna.com",
    "abbvie": "abbvie.com", "merck": "merck.com", "amgen": "amgen.com",
    "gilead": "gilead.com", "unitedhealth": "unitedhealthgroup.com",
    "exxonmobil": "exxonmobil.com", "chevron": "chevron.com",
    "shell": "shell.com", "bp": "bp.com", "reliance industries": "ril.com",
    "boeing": "boeing.com", "lockheed martin": "lockheedmartin.com",
    "caterpillar": "caterpillar.com", "honeywell": "honeywell.com",
    "3m": "3m.com", "fedex": "fedex.com", "ups": "ups.com",
    "walt disney": "disney.com", "disney": "disney.com",
    "warner bros": "warnerbros.com", "paramount": "paramount.com",
    "bloomberg": "bloomberg.com", "bloomberg lp": "bloomberg.com",
    "samsung": "samsung.com", "lg": "lg.com", "sony": "sony.com",
    "softbank": "softbank.com", "alibaba": "alibaba.com", "tencent": "tencent.com",
    "baidu": "baidu.com", "xiaomi": "xiaomi.com", "bytedance": "bytedance.com",
    "tata": "tata.com", "infosys": "infosys.com", "wipro": "wipro.com",
    "hcl": "hcl.com", "adani group": "adani.com",
    "lvmh": "lvmh.com", "loreal": "loreal.com", "l'oreal": "loreal.com",
    "hermes": "hermes.com", "inditex": "inditex.com", "zara": "zara.com",
    "siemens": "siemens.com", "sap": "sap.com", "allianz": "allianz.com",
    "ubs": "ubs.com", "novartis": "novartis.com", "roche": "roche.com",
    "paul mitchell": "paulmitchell.com", "fubu": "fubu.com",
    "corcoran group": "corcoran.com", "spanx": "spanx.com",
    "roc nation": "rocnation.com", "tyler perry studios": "tylerperry.com",
    "kylie cosmetics": "kyliecosmetics.com", "own network": "own.tv",
    "lucasfilm": "lucasfilm.com", "pixar": "pixar.com",
    "ethereum": "ethereum.org", "gemini": "gemini.com",
    "ripple": "ripple.com", "microstrategy": "microstrategy.com",
    "citadel": "citadel.com", "fidelity": "fidelity.com",
    "vanguard": "vanguard.com", "american express": "americanexpress.com",
    "visa": "visa.com", "mastercard": "mastercard.com",
    "verizon": "verizon.com", "att": "att.com", "at&t": "att.com",
    "t-mobile": "t-mobile.com", "comcast": "comcast.com",
    "lockheed martin": "lockheedmartin.com", "northrop grumman": "northropgrumman.com",
    "general dynamics": "gd.com", "raytheon": "raytheon.com",
    "ge": "ge.com", "general electric": "ge.com",
    "totalenergies": "totalenergies.com", "conocophillips": "conocophillips.com",
    "cvs health": "cvshealth.com", "cigna": "cigna.com",
    "bristol myers squibb": "bms.com", "eli lilly": "lilly.com",
    "regeneron": "regeneron.com", "biogen": "biogen.com",
    "schlumberger": "slb.com", "halliburton": "halliburton.com",
    "servicenow": "servicenow.com", "palantir": "palantir.com",
    "snowflake": "snowflake.com", "datadog": "datadoghq.com",
    "cloudflare": "cloudflare.com", "reddit": "reddit.com",
    "mozilla": "mozilla.org", "twilio": "twilio.com",
    "block": "block.xyz", "squareup": "squareup.com",
    "roc nation": "rocnation.com", "maverick": "maverick.com",
    "parkwood entertainment": "parkwood-entertainment.com",
    "fenty beauty": "fentybeauty.com", "p&g": "pg.com", "pg": "pg.com",
    "lyft": "lyft.com", "doordash": "doordash.com",
    "roku": "roku.com", "pinterest": "pinterest.com",
    "snap": "snap.com", "tiktok": "tiktok.com",
}

def find_domain(company):
    if not company: return None
    key = company.lower().strip()
    key = re.sub(r'[,\s]+', ' ', key).strip()
    if key in COMPANY_DOMAINS: return COMPANY_DOMAINS[key]
    for suffix in [' inc', ' corporation', ' corp', ' llc', ' ltd', ' limited', ' group', ' holdings', ' technologies', ', inc', ', llc']:
        stripped = key.replace(suffix, '').strip()
        if stripped in COMPANY_DOMAINS: return COMPANY_DOMAINS[stripped]
    first_word = key.split()[0] if key.split() else key
    if first_word in COMPANY_DOMAINS: return COMPANY_DOMAINS[first_word]
    domain = re.sub(r'[^a-zA-Z0-9]', '', key).strip()
    if domain and len(domain) > 2:
        return domain + '.com' if not domain.endswith('com') else domain
    return None

conn = sqlite3.connect(DB_PATH)
contacts = conn.execute(
    'SELECT id, name, company FROM contacts WHERE (email IS NULL OR email="") AND company IS NOT NULL AND company != ""'
).fetchall()
print(f"Processing {len(contacts)} contacts...")

updated = 0
for cid, name, company in contacts:
    domain = find_domain(company)
    if not domain: continue
    
    parts = name.strip().split()
    if len(parts) < 2: continue
    
    first = parts[0].lower()
    last = parts[-1].lower()
    
    # Generate first.last@domain (most common pattern)
    email = f"{first}.{last}@{domain}"
    conn.execute('UPDATE contacts SET email=?, email_source=? WHERE id=?',
                 (email, 'pattern:first.last@domain', cid))
    updated += 1

conn.commit()
total_with_email = conn.execute('SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ""').fetchone()[0]
conn.close()
print(f"Done! Updated {updated} contacts")
print(f"Total with email: {total_with_email}")
