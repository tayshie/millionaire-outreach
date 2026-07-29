import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'outreach.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def add_column(conn, table, column, coltype):
    try:
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {coltype}')
    except:
        pass

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER,
            name TEXT NOT NULL,
            net_worth REAL,
            wealth_tier TEXT DEFAULT 'millionaire',
            source TEXT,
            industry TEXT,
            country TEXT,
            state TEXT,
            city TEXT,
            age INTEGER,
            email TEXT,
            phone TEXT,
            company TEXT,
            title TEXT,
            linkedin_url TEXT,
            website_url TEXT,
            notes TEXT,
            tags TEXT,
            status TEXT DEFAULT 'new',
            email_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS contact_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            source_type TEXT,
            source_url TEXT,
            confidence REAL,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        );
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            target_count INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            open_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            donation_count INTEGER DEFAULT 0,
            donation_total REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            contact_id INTEGER,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            sent_at TIMESTAMP,
            opened_at TIMESTAMP,
            replied_at TIMESTAMP,
            reply_text TEXT,
            donated_amount REAL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        );
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        );
        CREATE TABLE IF NOT EXISTS import_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            rows_imported INTEGER,
            rows_skipped INTEGER,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_contacts_wealth_tier ON contacts(wealth_tier);
        CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
        CREATE INDEX IF NOT EXISTS idx_contacts_country ON contacts(country);
        CREATE INDEX IF NOT EXISTS idx_contacts_industry ON contacts(industry);
        CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
    ''')

    for col, ctype in [
        ("twitter_handle", "TEXT"), ("instagram_handle", "TEXT"),
        ("annual_revenue", "REAL"), ("employees", "INTEGER"),
        ("founded_year", "INTEGER"), ("funding_total", "REAL"),
        ("education", "TEXT"), ("philanthropy_focus", "TEXT"),
        ("source_url", "TEXT"), ("spouse", "TEXT"), ("children", "INTEGER"),
        ("residence", "TEXT"), ("board_memberships", "TEXT"),
    ]:
        add_column(conn, "contacts", col, ctype)

    conn.commit()
    conn.close()

def seed_templates():
    conn = get_db()
    existing = conn.execute('SELECT COUNT(*) FROM templates').fetchone()[0]
    if existing == 0:
        templates = [
            # ── HEARTSTRING / EMOTIONAL TEMPLATES ──
            ('The Hospital Room (Heartstring)', 'What I saw changed my perspective', '''{name},

I'm sitting in a hospital waiting room right now. Not for me — for my mother.

The woman next to me is crying because she can't afford her son's insulin. She works two jobs. He's 12 years old.

I started this project because I wanted to see if the wealthiest people in the world actually care. Not about tax breaks or portfolio diversification — but about people like her.

You're worth ${net_worth}B. You could end that woman's worry with what you spend on coffee this month.

I'm asking for just $5. To prove to that mother that someone out there gives a damn.

Will you be the person who proves it?

{payment_links}

With hope,
[Your Name]'''),

            ('The Letter My Father Never Got', 'A story about time', '''Dear {name},

My father died last year. Not from a disease — from exhaustion. He worked himself into the ground trying to give us a better life. He never had help.

I think about what would have happened if just one wealthy person had reached out to him. Just once. To say "I see you. I believe in you."

I'm asking you to be that person for someone else.

$5 from you. Combined with thousands of others like you. Given to people who just need a break.

The world doesn't need another billionaire. It needs a thousand helping hands.

{payment_links}

{name}'''),

            ('The $5 Question That Keeps Me Up at Night', 'Will you answer?', '''{name},

Here's what keeps me up at night:

If the wealthiest 3,000 people gave just $5 a week to someone in need, they'd move $60M+ per year into communities that desperately need it.

That's not charity. That's pocket change for you.

I'm asking for $5. One time. To prove that the wealthy will engage with ordinary people when asked directly and honestly.

You're #{rank} in my outreach list. I've contacted {responses_count} others. Some said yes. Most ignored me.

Will you be a yes?

{payment_links}

Respectfully,
[Your Name]'''),

            ('The Server at the Diner', 'She reminded me why I\'m doing this', '''{name},

Last week, a waitress served me coffee at a diner in Ohio. She was 62. Her hands shook from arthritis. She told me she's been working since she was 16 and still can't afford to retire.

I paid for my coffee and left. I should have done more.

So I'm doing this instead.

I'm reaching out to every wealthy person I can find. Not to shame you — to invite you. To be part of a movement where the richest people on earth prove they still have hearts.

$5. That's the ask. A cup of coffee's worth of kindness from someone who could buy the whole chain.

{payment_links}

Gracefully,
[Your Name]'''),

            ('What Would You Tell Your Younger Self?', 'A personal question', '''{name},

If you could go back 20 years and tell your younger self one thing, what would it be?

Mine would be: "There are wealthy people who want to help. You just have to ask."

I'm asking. Not for a fortune. For $5.

Because I want my younger self — and every other struggling person — to know that the wealthy aren't just names on a Forbes list. They're people who can change a life with their spare change.

Be the person my younger self needed.

{payment_links}

{name}'''),

            ('The Last Time Someone Helped You', 'Pay it forward', '''{name},

Think about the last time someone helped you when you really needed it.

Who was it? What did they do? How did it feel?

Now imagine being that person for someone else. With $5.

I'm not asking you to write a million-dollar check. I'm asking you to participate in a micro-experiment: what happens when 10,000 wealthy people each give $5 to one person they'll never meet?

History happens. That's what.

Be part of the first page.

{payment_links}

With gratitude,
[Your Name]'''),

            ('The 3 AM Email', 'I couldn\'t sleep thinking about this', '''{name},

It's 3 AM. I should be sleeping. Instead, I'm writing to you.

I've been thinking about how strange wealth inequality has become. You have more money than you could spend in 10 lifetimes. There are people who will die because they can't afford $5 medicine.

And somehow, the gap between those two realities doesn't seem to bother most people.

It bothers me.

So I'm doing something about it. One email at a time. Starting with you.

${net_worth}B in net worth. $5 asked. You do the math on whether that's fair.

I'm not here for fair. I'm here to see if you care.

{payment_links}

Sleeplessly,
[Your Name]'''),

            ('The Obituary That Broke Me', 'I read it and couldn\'t move', '''{name},

I read an obituary last week. A woman, 45. Died from a treatable illness because she couldn't afford the medication.

She left behind three kids. Her last words to her daughter: "I'm sorry I couldn't fight harder."

{name} — she fought plenty hard. The system failed her. Not because the money doesn't exist. Because the people with it never knew she existed.

I'm trying to change that. One email. One $5 ask. One wealthy person at a time.

Will you help me prove that the wealthy DO know — and DO care?

{payment_links}

{name}'''),
        ]
        conn.executemany(
            'INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)',
            templates
        )
        conn.commit()
    conn.close()

def seed_sample_contacts():
    conn = get_db()
    existing = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    if existing == 0:
        try:
            from seed_data import generate_contacts
            contacts = generate_contacts(5000)
            count = 0
            for c in contacts:
                conn.execute(
                    '''INSERT INTO contacts (rank, name, net_worth, wealth_tier, source, industry, country, state, city, age, company)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                    (c.get('rank', 0), c['name'], c.get('net_worth', 0), c.get('wealth_tier', 'millionaire'),
                     c.get('source', ''), c.get('industry', ''), c.get('country', ''),
                     c.get('state', ''), c.get('city', ''), c.get('age'), c.get('company', ''))
                )
                count += 1
            conn.commit()
            print(f"[*] Seeded {count} contacts from seed_data")
        except Exception as e:
            print(f"[-] Failed to load seed_data: {e}, using backup...")
            billionaires = [
                (1, 'Elon Musk', 839.0, 'billionaire', 'Tesla, SpaceX', 'Technology', 'United States', 'TX', 'Austin', 54, 'Tesla'),
                (2, 'Bernard Arnault', 198.0, 'billionaire', 'LVMH', 'Fashion & Retail', 'France', '', 'Paris', 76, 'LVMH'),
                (3, 'Jeff Bezos', 194.0, 'billionaire', 'Amazon', 'Technology', 'United States', 'WA', 'Medina', 61, 'Amazon'),
                (4, 'Mark Zuckerberg', 177.0, 'billionaire', 'Meta', 'Technology', 'United States', 'CA', 'Palo Alto', 41, 'Meta'),
                (5, 'Warren Buffett', 157.0, 'billionaire', 'Berkshire Hathaway', 'Finance', 'United States', 'NE', 'Omaha', 94, 'Berkshire Hathaway'),
                (6, 'Bill Gates', 148.0, 'billionaire', 'Microsoft', 'Technology', 'United States', 'WA', 'Medina', 69, 'Microsoft'),
                (7, 'Larry Page', 142.0, 'billionaire', 'Google', 'Technology', 'United States', 'CA', 'Palo Alto', 52, 'Alphabet'),
                (8, 'Sergey Brin', 136.0, 'billionaire', 'Google', 'Technology', 'United States', 'CA', 'Los Altos', 50, 'Alphabet'),
                (9, 'Mukesh Ambani', 125.0, 'billionaire', 'Reliance Industries', 'Energy', 'India', '', 'Mumbai', 68, 'Reliance'),
                (10, 'Michael Bloomberg', 120.0, 'billionaire', 'Bloomberg LP', 'Finance', 'United States', 'NY', 'New York', 83, 'Bloomberg'),
            ]
            conn.executemany(
                'INSERT INTO contacts (rank, name, net_worth, wealth_tier, source, industry, country, state, city, age, company) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                billionaires
            )
            conn.commit()
    conn.close()
