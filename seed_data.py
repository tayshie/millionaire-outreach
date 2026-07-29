"""Massive seed dataset of known wealthy individuals from public sources.
Combines real known billionaires, executives, celebrities with generated contacts using real company/industry/country data.
Aims for 5000+ total contacts spanning all wealth tiers."""

import random
import math

# ── REAL KNOWN BILLIONAIRES (Forbes top, compact format) ──
# (name, net_worth_b, source, industry, country, state, city, age, company)
BILLIONAIRES = [
    ("Bernard Arnault", 233.0, "LVMH", "Fashion & Retail", "France", "", "Paris", 76, "LVMH"),
    ("Elon Musk", 195.0, "Tesla, SpaceX", "Technology", "United States", "TX", "Austin", 54, "Tesla"),
    ("Jeff Bezos", 194.0, "Amazon", "Technology", "United States", "WA", "Medina", 61, "Amazon"),
    ("Mark Zuckerberg", 177.0, "Meta", "Technology", "United States", "CA", "Palo Alto", 41, "Meta"),
    ("Larry Ellison", 151.0, "Oracle", "Technology", "United States", "CA", "Woodside", 80, "Oracle"),
    ("Warren Buffett", 157.0, "Berkshire Hathaway", "Finance", "United States", "NE", "Omaha", 94, "Berkshire Hathaway"),
    ("Bill Gates", 148.0, "Microsoft", "Technology", "United States", "WA", "Medina", 69, "Microsoft"),
    ("Larry Page", 142.0, "Google", "Technology", "United States", "CA", "Palo Alto", 52, "Alphabet"),
    ("Sergey Brin", 136.0, "Google", "Technology", "United States", "CA", "Los Altos", 50, "Alphabet"),
    ("Steve Ballmer", 123.0, "Microsoft", "Technology", "United States", "WA", "Hunts Point", 69, "Microsoft"),
    ("Mukesh Ambani", 125.0, "Reliance Industries", "Energy", "India", "", "Mumbai", 68, "Reliance"),
    ("Michael Bloomberg", 120.0, "Bloomberg LP", "Finance", "United States", "NY", "New York", 83, "Bloomberg LP"),
    ("Carlos Slim Helu", 102.0, "America Movil", "Telecommunications", "Mexico", "", "Mexico City", 85, "Grupo Carso"),
    ("Francoise Bettencourt Meyers", 99.0, "L'Oreal", "Consumer Goods", "France", "", "Paris", 71, "L'Oreal"),
    ("Amancio Ortega", 98.0, "Zara/Inditex", "Fashion & Retail", "Spain", "", "La Coruna", 89, "Inditex"),
    ("Michael Dell", 91.0, "Dell Technologies", "Technology", "United States", "TX", "Austin", 60, "Dell"),
    ("Charles Koch", 86.0, "Koch Industries", "Diversified", "United States", "KS", "Wichita", 90, "Koch Industries"),
    ("Julia Koch", 86.0, "Koch Industries", "Diversified", "United States", "NY", "New York", 63, "Koch Industries"),
    ("Gautam Adani", 84.0, "Adani Group", "Infrastructure", "India", "", "Ahmedabad", 61, "Adani Group"),
    ("Jim Walton", 82.0, "Walmart", "Fashion & Retail", "United States", "AR", "Bentonville", 77, "Walmart"),
    ("Alice Walton", 78.0, "Walmart", "Fashion & Retail", "United States", "TX", "Fort Worth", 76, "Walmart"),
    ("Rob Walton", 76.0, "Walmart", "Fashion & Retail", "United States", "AR", "Bentonville", 81, "Walmart"),
    ("David Thomson", 67.0, "Thomson Reuters", "Media", "Canada", "ON", "Toronto", 66, "Thomson Reuters"),
    ("Jensen Huang", 62.0, "NVIDIA", "Technology", "United States", "CA", "Los Altos", 62, "NVIDIA"),
    ("Mackenzie Scott", 59.0, "Amazon", "Technology", "United States", "WA", "Seattle", 54, "Amazon"),
    ("Phil Knight", 57.0, "Nike", "Consumer Goods", "United States", "OR", "Beaverton", 87, "Nike"),
    ("Changpeng Zhao", 55.0, "Binance", "Cryptocurrency", "Canada", "ON", "Toronto", 48, "Binance"),
    ("Colin Huang", 54.0, "Pinduoduo", "Technology", "China", "", "Shanghai", 45, "PDD Holdings"),
    ("Tadashi Yanai", 54.0, "Uniqlo", "Fashion & Retail", "Japan", "", "Tokyo", 76, "Fast Retailing"),
    ("Klaus-Michael Kuehne", 52.0, "Kuehne+Nagel", "Logistics", "Germany", "", "Hamburg", 87, "Kuehne+Nagel"),
    ("Zhong Shanshan", 51.0, "Nongfu Spring", "Consumer Goods", "China", "", "Hangzhou", 71, "Nongfu Spring"),
    ("Zhang Yiming", 50.0, "ByteDance", "Technology", "China", "", "Beijing", 42, "ByteDance"),
    ("Miriam Adelson", 48.0, "Las Vegas Sands", "Gaming", "United States", "NV", "Las Vegas", 79, "Las Vegas Sands"),
    ("Leonid Mikhelson", 47.0, "Novatek", "Energy", "Russia", "", "Moscow", 69, "Novatek"),
    ("Vladimir Potanin", 46.0, "Norilsk Nickel", "Mining", "Russia", "", "Moscow", 64, "Norilsk Nickel"),
    ("Gina Rinehart", 45.0, "Hancock Prospecting", "Mining", "Australia", "", "Perth", 71, "Hancock Prospecting"),
    ("Vladimir Lisin", 44.0, "NLMK", "Steel", "Russia", "", "Moscow", 68, "NLMK"),
    ("Reinhold Wuerth", 43.0, "Wuerth Group", "Manufacturing", "Germany", "", "Kuenzelsau", 90, "Wuerth Group"),
    ("Eric Schmidt", 42.0, "Google", "Technology", "United States", "CA", "Atherton", 70, "Alphabet"),
    ("Vicky Safra", 41.0, "Safra Group", "Banking", "Brazil", "", "Sao Paulo", 72, "Safra Group"),
    ("Li Ka-shing", 40.0, "CK Hutchison", "Diversified", "Hong Kong", "", "Hong Kong", 96, "CK Hutchison"),
    ("Nicky Oppenheimer", 39.0, "De Beers", "Mining", "South Africa", "", "Johannesburg", 80, "De Beers"),
    ("James Ratcliffe", 38.0, "Ineos", "Chemicals", "United Kingdom", "", "London", 72, "Ineos"),
    ("Alisher Usmanov", 37.0, "Metalloinvest", "Mining", "Russia", "", "Moscow", 70, "Metalloinvest"),
    ("Gennady Timchenko", 36.0, "Volga Group", "Energy", "Russia", "", "Moscow", 72, "Volga Group"),
    ("Mikhail Fridman", 35.0, "Alfa Group", "Finance", "Russia", "", "Moscow", 60, "Alfa Group"),
    ("German Larrea Mota Velasco", 34.0, "Grupo Mexico", "Mining", "Mexico", "", "Mexico City", 71, "Grupo Mexico"),
    ("Patrick Soon-Shiong", 33.0, "Pharma", "Healthcare", "United States", "CA", "Los Angeles", 73, "NantWorks"),
    ("Thomas Peterffy", 32.0, "Interactive Brokers", "Finance", "United States", "FL", "Palm Beach", 80, "Interactive Brokers"),
    ("John Menard Jr", 31.0, "Menards", "Fashion & Retail", "United States", "WI", "Eau Claire", 85, "Menards"),
    ("Michele Ferrero", 30.0, "Ferrero", "Consumer Goods", "Italy", "", "Alba", 98, "Ferrero"),
    ("Ralph Lauren", 29.0, "Ralph Lauren", "Fashion", "United States", "NY", "New York", 85, "Ralph Lauren Corporation"),
    ("David Geffen", 28.0, "Geffen Records", "Entertainment", "United States", "CA", "Malibu", 82, "Geffen Records"),
    ("Gordon Getty", 27.0, "Getty Oil", "Energy", "United States", "CA", "San Francisco", 92, "Getty Family"),
    ("Roman Abramovich", 26.0, "Millhouse LLC", "Finance", "Russia", "", "Moscow", 58, "Millhouse"),
    ("John Paulson", 25.0, "Paulson & Co", "Finance", "United States", "NY", "New York", 69, "Paulson & Co"),
    ("Stephen Schwarzman", 24.0, "Blackstone", "Finance", "United States", "NY", "New York", 78, "Blackstone Group"),
    ("Leon Black", 23.0, "Apollo Global", "Finance", "United States", "NY", "New York", 73, "Apollo Global Management"),
    ("Henry Kravis", 22.0, "KKR", "Finance", "United States", "NY", "New York", 81, "KKR"),
    ("David Rubenstein", 21.0, "Carlyle Group", "Finance", "United States", "MD", "Bethesda", 75, "Carlyle Group"),
    ("Ted Turner", 20.0, "CNN", "Media", "United States", "GA", "Atlanta", 86, "Turner Broadcasting"),
    ("Rupert Murdoch", 19.0, "News Corp", "Media", "United States", "NY", "New York", 94, "News Corp"),
    ("Sumner Redstone", 18.0, "ViacomCBS", "Media", "United States", "CA", "Los Angeles", 102, "National Amusements"),
    ("Oprah Winfrey", 28.0, "OWN", "Media", "United States", "CA", "Montecito", 71, "OWN Network"),
    ("George Soros", 17.0, "Soros Fund", "Finance", "United States", "NY", "New York", 94, "Soros Fund Management"),
    ("Ray Dalio", 16.0, "Bridgewater", "Finance", "United States", "CT", "Greenwich", 75, "Bridgewater Associates"),
    ("Carl Icahn", 15.0, "Icahn Enterprises", "Finance", "United States", "NY", "New York", 89, "Icahn Enterprises"),
    ("Ken Griffin", 14.0, "Citadel", "Finance", "United States", "FL", "Miami", 56, "Citadel LLC"),
    ("Jack Dorsey", 13.0, "Twitter, Block", "Technology", "United States", "CA", "San Francisco", 48, "Block Inc"),
    ("Travis Kalanick", 12.0, "Uber", "Technology", "United States", "CA", "San Francisco", 49, "Uber"),
    ("Brian Chesky", 11.0, "Airbnb", "Technology", "United States", "CA", "San Francisco", 43, "Airbnb"),
    ("Sam Altman", 10.0, "OpenAI", "Technology", "United States", "CA", "San Francisco", 40, "OpenAI"),
    ("Drew Houston", 9.5, "Dropbox", "Technology", "United States", "CA", "San Francisco", 42, "Dropbox"),
    ("Daniel Ek", 8.5, "Spotify", "Technology", "Sweden", "", "Stockholm", 42, "Spotify"),
    ("Patrick Collison", 8.0, "Stripe", "Technology", "Ireland", "", "Dublin", 36, "Stripe"),
    ("John Collison", 7.5, "Stripe", "Technology", "Ireland", "", "Dublin", 34, "Stripe"),
    ("Vitalik Buterin", 6.5, "Ethereum", "Cryptocurrency", "Canada", "", "Toronto", 31, "Ethereum"),
    ("Brian Armstrong", 6.0, "Coinbase", "Cryptocurrency", "United States", "CA", "San Francisco", 42, "Coinbase"),
    ("Cameron Winklevoss", 5.5, "Gemini", "Cryptocurrency", "United States", "NY", "New York", 43, "Gemini"),
    ("Tyler Winklevoss", 5.5, "Gemini", "Cryptocurrency", "United States", "NY", "New York", 43, "Gemini"),
    ("Barry Silbert", 5.0, "Digital Currency Group", "Cryptocurrency", "United States", "NY", "New York", 49, "DCG"),
    ("Tony Hsieh", 4.5, "Zappos", "Technology", "United States", "NV", "Las Vegas", 46, "Zappos"),
    ("Pierre Omidyar", 4.0, "eBay", "Technology", "United States", "HI", "Honolulu", 58, "eBay"),
    ("Mark Cuban", 3.5, "Investments", "Finance", "United States", "TX", "Dallas", 66, "Dallas Mavericks"),
    ("Kevin O'Leary", 4.2, "Investments", "Finance", "Canada", "ON", "Toronto", 71, "O'Leary Ventures"),
    ("Barbara Corcoran", 1.8, "Real Estate", "Real Estate", "United States", "NY", "New York", 76, "Corcoran Group"),
    ("Daymond John", 2.5, "FUBU", "Fashion", "United States", "NY", "New York", 56, "FUBU"),
    ("Sara Blakely", 11.0, "Spanx", "Fashion", "United States", "GA", "Atlanta", 54, "Spanx"),
    ("Kylie Jenner", 7.0, "Kylie Cosmetics", "Consumer Goods", "United States", "CA", "Hidden Hills", 28, "Kylie Cosmetics"),
    ("Jay-Z", 25.0, "Music, Investments", "Entertainment", "United States", "NY", "New York", 56, "Roc Nation"),
    ("Tyler Perry", 8.0, "Entertainment", "Media", "United States", "GA", "Atlanta", 55, "Tyler Perry Studios"),
    ("George Lucas", 55.0, "Star Wars", "Entertainment", "United States", "CA", "San Francisco", 81, "Lucasfilm"),
    ("Steve Jobs (estate)", 47.0, "Apple, Pixar", "Technology", "United States", "CA", "Palo Alto", 69, "Apple"),
    ("Paul Allen (estate)", 34.0, "Microsoft", "Technology", "United States", "WA", "Seattle", 65, "Vulcan"),
]

# ── REAL FORTUNE 500 CEOS & EXECUTIVES ──
EXECUTIVES = [
    ("Tim Cook", 0.5, "Apple", "Technology", "United States", "CA", "Cupertino", 64, "Apple"),
    ("Satya Nadella", 0.4, "Microsoft", "Technology", "United States", "WA", "Redmond", 57, "Microsoft"),
    ("Sundar Pichai", 0.6, "Google", "Technology", "United States", "CA", "Mountain View", 53, "Alphabet"),
    ("Andy Jassy", 0.3, "Amazon", "Technology", "United States", "WA", "Seattle", 57, "Amazon"),
    ("Warren Buffett", 157.0, "Berkshire Hathaway", "Finance", "United States", "NE", "Omaha", 94, "Berkshire Hathaway"),
    ("Jamie Dimon", 0.5, "JPMorgan Chase", "Finance", "United States", "NY", "New York", 69, "JPMorgan Chase"),
    ("David Solomon", 0.3, "Goldman Sachs", "Finance", "United States", "NY", "New York", 63, "Goldman Sachs"),
    ("James Gorman", 0.4, "Morgan Stanley", "Finance", "United States", "NY", "New York", 66, "Morgan Stanley"),
    ("Brian Moynihan", 0.2, "Bank of America", "Finance", "United States", "NC", "Charlotte", 65, "Bank of America"),
    ("Jane Fraser", 0.2, "Citigroup", "Finance", "United States", "NY", "New York", 57, "Citigroup"),
    ("Charles Scharf", 0.2, "Wells Fargo", "Finance", "United States", "CA", "San Francisco", 60, "Wells Fargo"),
    ("Bob Iger", 0.4, "Disney", "Media", "United States", "CA", "Burbank", 74, "Disney"),
    ("David Zaslav", 0.3, "Warner Bros Discovery", "Media", "United States", "NY", "New York", 65, "Warner Bros Discovery"),
    ("Ted Sarandos", 0.2, "Netflix", "Technology", "United States", "CA", "Los Gatos", 60, "Netflix"),
    ("Bob Chapek", 0.1, "Disney", "Media", "United States", "CA", "Burbank", 65, "Disney"),
    ("Mary Barra", 0.3, "General Motors", "Automotive", "United States", "MI", "Detroit", 63, "General Motors"),
    ("Jim Farley", 0.2, "Ford Motor", "Automotive", "United States", "MI", "Dearborn", 62, "Ford"),
    ("Elon Musk", 195.0, "Tesla", "Automotive", "United States", "TX", "Austin", 54, "Tesla"),
    ("Doug McMillon", 0.2, "Walmart", "Fashion & Retail", "United States", "AR", "Bentonville", 58, "Walmart"),
    ("Brian Cornell", 0.2, "Target", "Fashion & Retail", "United States", "MN", "Minneapolis", 66, "Target"),
    ("Rodney McMullen", 0.1, "Kroger", "Fashion & Retail", "United States", "OH", "Cincinnati", 64, "Kroger"),
    ("Andy Jassy", 0.3, "Amazon", "Technology", "United States", "WA", "Seattle", 57, "Amazon"),
    ("John Donahoe", 0.2, "Nike", "Consumer Goods", "United States", "OR", "Beaverton", 64, "Nike"),
    ("Laxman Narasimhan", 0.1, "Starbucks", "Consumer Goods", "United States", "WA", "Seattle", 58, "Starbucks"),
    ("Ramon Laguarta", 0.2, "PepsiCo", "Consumer Goods", "United States", "NY", "Purchase", 61, "PepsiCo"),
    ("James Quincey", 0.2, "Coca-Cola", "Consumer Goods", "United States", "GA", "Atlanta", 60, "Coca-Cola"),
    ("Chris Kempczinski", 0.2, "McDonald's", "Consumer Goods", "United States", "IL", "Chicago", 58, "McDonald's"),
    ("David Taylor", 0.2, "Procter & Gamble", "Consumer Goods", "United States", "OH", "Cincinnati", 65, "P&G"),
    ("Larry Fink", 0.9, "BlackRock", "Finance", "United States", "NY", "New York", 72, "BlackRock"),
    ("Abigail Johnson", 12.0, "Fidelity", "Finance", "United States", "MA", "Boston", 63, "Fidelity Investments"),
    ("Aditya Mittal", 0.3, "ArcelorMittal", "Steel", "India", "", "Mumbai", 49, "ArcelorMittal"),
    ("Lakshmi Mittal", 15.0, "ArcelorMittal", "Steel", "India", "", "London", 74, "ArcelorMittal"),
    ("Anil Agarwal", 3.0, "Vedanta", "Mining", "India", "", "Mumbai", 71, "Vedanta Resources"),
    ("Kumar Birla", 7.0, "Aditya Birla", "Diversified", "India", "", "Mumbai", 57, "Aditya Birla Group"),
    ("Uday Kotak", 5.0, "Kotak Mahindra", "Finance", "India", "", "Mumbai", 66, "Kotak Mahindra Bank"),
    ("Cyrus Poonawalla", 8.0, "Serum Institute", "Healthcare", "India", "", "Pune", 84, "Serum Institute"),
    ("Shiv Nadar", 6.0, "HCL", "Technology", "India", "", "New Delhi", 79, "HCL Technologies"),
    ("Radhakishan Damani", 5.0, "DMart", "Fashion & Retail", "India", "", "Mumbai", 70, "Avenue Supermarts"),
    ("Masayoshi Son", 25.0, "SoftBank", "Technology", "Japan", "", "Tokyo", 67, "SoftBank Group"),
    ("Tadashi Yanai", 54.0, "Uniqlo", "Fashion & Retail", "Japan", "", "Tokyo", 76, "Fast Retailing"),
    ("Jack Ma", 30.0, "Alibaba", "Technology", "China", "", "Hangzhou", 60, "Alibaba Group"),
    ("Pony Ma", 42.0, "Tencent", "Technology", "China", "", "Shenzhen", 53, "Tencent"),
    ("Robin Li", 18.0, "Baidu", "Technology", "China", "", "Beijing", 56, "Baidu"),
    ("William Ding", 25.0, "NetEase", "Technology", "China", "", "Guangzhou", 53, "NetEase"),
    ("Lei Jun", 25.0, "Xiaomi", "Technology", "China", "", "Beijing", 55, "Xiaomi"),
    ("Zhang Yiming", 50.0, "ByteDance", "Technology", "China", "", "Beijing", 42, "ByteDance"),
    ("Daniel Zhang", 5.0, "Alibaba", "Technology", "China", "", "Hangzhou", 53, "Alibaba Group"),
    ("Wang Xing", 20.0, "Meituan", "Technology", "China", "", "Beijing", 46, "Meituan"),
    ("Huang Zheng", 54.0, "Pinduoduo", "Technology", "China", "", "Shanghai", 45, "PDD Holdings"),
    ("Liu Qiangdong", 15.0, "JD.com", "Technology", "China", "", "Beijing", 51, "JD.com"),
    ("Sun Piaoyang", 10.0, "Hengrui Pharma", "Healthcare", "China", "", "Lianyungang", 66, "Hengrui Medicine"),
    ("Li Shufu", 8.0, "Geely", "Automotive", "China", "", "Hangzhou", 62, "Geely Holding"),
    ("He Xiangjian", 16.0, "Midea", "Manufacturing", "China", "", "Foshan", 83, "Midea Group"),
    ("Lu Zhiqiang", 14.0, "Oceanwide", "Real Estate", "China", "", "Beijing", 72, "Oceanwide Holdings"),
    ("Xu Jiayin", 12.0, "Evergrande", "Real Estate", "China", "", "Guangzhou", 66, "Evergrande Group"),
    ("Wang Jianlin", 10.0, "Dalian Wanda", "Real Estate", "China", "", "Beijing", 70, "Wanda Group"),
    ("Hui Ka Yan", 8.0, "Evergrande", "Real Estate", "China", "", "Guangzhou", 66, "Evergrande Group"),
    ("Yang Huiyan", 7.0, "Country Garden", "Real Estate", "China", "", "Foshan", 44, "Country Garden"),
    ("Dangelo Russell", 0.05, "NBA", "Sports", "United States", "CA", "Los Angeles", 29, "Los Angeles Lakers"),
]

# ── SPORTS STARS ──
SPORTS = [
    ("Michael Jordan", 3.2, "NBA, Nike", "Sports", "United States", "NC", "Charlotte", 62, "Charlotte Hornets"),
    ("LeBron James", 1.2, "NBA, Endorsements", "Sports", "United States", "CA", "Los Angeles", 40, "Los Angeles Lakers"),
    ("Tiger Woods", 1.1, "Golf, Endorsements", "Sports", "United States", "FL", "Jupiter", 49, "TGR Foundation"),
    ("Cristiano Ronaldo", 0.9, "Football, Endorsements", "Sports", "Portugal", "", "Lisbon", 40, "Al Nassr"),
    ("Lionel Messi", 0.8, "Football, Endorsements", "Sports", "Argentina", "", "Buenos Aires", 38, "Inter Miami"),
    ("Roger Federer", 0.8, "Tennis, Endorsements", "Sports", "Switzerland", "", "Zurich", 43, "RF Foundation"),
    ("Floyd Mayweather", 0.6, "Boxing", "Sports", "United States", "NV", "Las Vegas", 48, "Mayweather Promotions"),
    ("Tom Brady", 0.5, "NFL, Endorsements", "Sports", "United States", "FL", "Tampa", 47, "TB12 Sports"),
    ("Stephen Curry", 0.4, "NBA, Endorsements", "Sports", "United States", "CA", "San Francisco", 37, "Golden State Warriors"),
    ("Kevin Durant", 0.3, "NBA, Investments", "Sports", "United States", "CA", "San Francisco", 36, "Phoenix Suns"),
    ("Giannis Antetokounmpo", 0.2, "NBA", "Sports", "Greece", "", "Athens", 30, "Milwaukee Bucks"),
    ("Neymar Jr", 0.3, "Football, Endorsements", "Sports", "Brazil", "", "Sao Paulo", 33, "Al Hilal"),
    ("Serena Williams", 0.3, "Tennis, Endorsements", "Sports", "United States", "FL", "Palm Beach", 43, "Serena Ventures"),
    ("Phil Mickelson", 0.4, "Golf", "Sports", "United States", "CA", "San Diego", 55, "LIV Golf"),
    ("Dwayne Johnson", 0.8, "Wrestling, Acting", "Sports", "United States", "FL", "Miami", 53, "Seven Bucks Productions"),
    ("Conor McGregor", 0.3, "MMA, Business", "Sports", "Ireland", "", "Dublin", 36, "Proper No. Twelve"),
    ("Lewis Hamilton", 0.4, "F1, Endorsements", "Sports", "United Kingdom", "", "London", 40, "Mercedes F1"),
    ("Max Verstappen", 0.2, "F1", "Sports", "Netherlands", "", "Monte Carlo", 27, "Red Bull Racing"),
    ("Shaquille O'Neal", 0.5, "NBA, Endorsements", "Sports", "United States", "FL", "Orlando", 53, "Shaq Inc"),
    ("Magic Johnson", 0.6, "NBA, Business", "Sports", "United States", "CA", "Los Angeles", 65, "Magic Johnson Enterprises"),
    ("David Beckham", 0.5, "Football, Endorsements", "Sports", "United Kingdom", "", "London", 50, "Inter Miami CF"),
    ("Kobe Bryant (estate)", 0.7, "NBA, Endorsements", "Sports", "United States", "CA", "Los Angeles", 41, "Kobe Inc"),
    ("Dirk Nowitzki", 0.2, "NBA", "Sports", "Germany", "", "Wurzburg", 47, "Dallas Mavericks"),
    ("Michael Phelps", 0.1, "Swimming, Endorsements", "Sports", "United States", "AZ", "Phoenix", 40, "MP Inc"),
    ("Usain Bolt", 0.1, "Track, Endorsements", "Sports", "Jamaica", "", "Kingston", 38, "Bolt Entertainment"),
]

# ── ENTERTAINERS ──
ENTERTAINERS = [
    ("George Lucas", 55.0, "Star Wars", "Entertainment", "United States", "CA", "San Francisco", 81, "Lucasfilm"),
    ("Steven Spielberg", 4.0, "Movies", "Entertainment", "United States", "CA", "Los Angeles", 78, "Amblin Entertainment"),
    ("James Cameron", 1.5, "Movies", "Entertainment", "Canada", "", "Los Angeles", 70, "Lightstorm Entertainment"),
    ("Peter Jackson", 1.2, "Movies", "Entertainment", "New Zealand", "", "Wellington", 63, "Wingnut Films"),
    ("Ridley Scott", 1.0, "Movies", "Entertainment", "United Kingdom", "", "London", 87, "Scott Free Productions"),
    ("Christopher Nolan", 0.8, "Movies", "Entertainment", "United Kingdom", "", "Los Angeles", 55, "Syncopy"),
    ("J.K. Rowling", 1.0, "Harry Potter", "Entertainment", "United Kingdom", "", "Edinburgh", 59, "Harry Potter franchise"),
    ("Stephen King", 0.6, "Books, Movies", "Entertainment", "United States", "ME", "Bangor", 77, "Stephen King Properties"),
    ("James Patterson", 0.4, "Books", "Entertainment", "United States", "FL", "Palm Beach", 78, "James Patterson"),
    ("Oprah Winfrey", 28.0, "Media", "Media", "United States", "CA", "Montecito", 71, "OWN Network"),
    ("Ellen DeGeneres", 0.5, "TV", "Entertainment", "United States", "CA", "Montecito", 67, "Ellen Digital Ventures"),
    ("Dr. Phil McGraw", 0.6, "TV", "Media", "United States", "TX", "Dallas", 74, "Phil McGraw"),
    ("Jerry Seinfeld", 1.0, "Comedy, TV", "Entertainment", "United States", "NY", "New York", 71, "Seinfeld"),
    ("Larry David", 0.9, "Comedy, TV", "Entertainment", "United States", "CA", "Los Angeles", 77, "Curb Your Enthusiasm"),
    ("Matt Groening", 0.6, "The Simpsons", "Entertainment", "United States", "CA", "Los Angeles", 71, "The Simpsons"),
    ("Seth MacFarlane", 0.3, "Family Guy", "Entertainment", "United States", "CA", "Los Angeles", 51, "Fuzzy Door Productions"),
    ("Ryan Murphy", 0.3, "TV", "Entertainment", "United States", "CA", "Los Angeles", 59, "Ryan Murphy Productions"),
    ("Shonda Rhimes", 0.3, "TV", "Entertainment", "United States", "CA", "Los Angeles", 55, "Shondaland"),
    ("Tyler Perry", 8.0, "Movies, TV", "Entertainment", "United States", "GA", "Atlanta", 55, "Tyler Perry Studios"),
    ("Beyonce", 0.8, "Music", "Entertainment", "United States", "NY", "New York", 43, "Parkwood Entertainment"),
    ("Jay-Z", 25.0, "Music, Investments", "Entertainment", "United States", "NY", "New York", 56, "Roc Nation"),
    ("Taylor Swift", 1.0, "Music", "Entertainment", "United States", "NY", "New York", 35, "Taylor Swift Productions"),
    ("Kanye West", 2.0, "Music, Fashion", "Entertainment", "United States", "CA", "Los Angeles", 47, "Yeezy"),
    ("Rihanna", 1.4, "Music, Beauty", "Entertainment", "Barbados", "", "Bridgetown", 37, "Fenty Beauty"),
    ("Madonna", 0.8, "Music", "Entertainment", "United States", "NY", "New York", 66, "Maverick"),
    ("Paul McCartney", 1.2, "Music", "Entertainment", "United Kingdom", "", "London", 83, "MPL Communications"),
    ("Bruce Springsteen", 0.7, "Music", "Entertainment", "United States", "NJ", "Freehold", 75, "Bruce Springsteen"),
    ("Bob Dylan", 0.6, "Music", "Entertainment", "United States", "NY", "New York", 84, "Bob Dylan"),
    ("Dr. Dre", 0.5, "Music, Beats", "Entertainment", "United States", "CA", "Los Angeles", 60, "Aftermath Entertainment"),
    ("Jimmy Iovine", 0.4, "Music, Beats", "Entertainment", "United States", "CA", "Los Angeles", 72, "Interscope Records"),
    ("Simon Cowell", 0.5, "TV, Music", "Entertainment", "United Kingdom", "", "London", 65, "Syco Entertainment"),
    ("Tom Cruise", 0.6, "Movies", "Entertainment", "United States", "CA", "Los Angeles", 63, "Cruise/Wagner Productions"),
    ("Robert Downey Jr", 0.3, "Movies", "Entertainment", "United States", "CA", "Los Angeles", 60, "Downey Studios"),
    ("Jerry Bruckheimer", 0.8, "Movies, TV", "Entertainment", "United States", "CA", "Los Angeles", 81, "Jerry Bruckheimer Films"),
    ("Dick Wolf", 0.5, "TV", "Entertainment", "United States", "NY", "New York", 79, "Wolf Entertainment"),
    ("Mark Burnett", 0.4, "TV", "Entertainment", "United States", "CA", "Los Angeles", 64, "MGM Television"),
    ("Gordon Ramsay", 0.2, "TV, Restaurants", "Entertainment", "United Kingdom", "", "London", 58, "Gordon Ramsay Holdings"),
    ("Martha Stewart", 0.3, "Lifestyle", "Media", "United States", "NY", "New York", 83, "Martha Stewart Living"),
    ("Rachael Ray", 0.2, "TV, Cooking", "Entertainment", "United States", "NY", "Lake Luzerne", 56, "Rachael Ray"),
    ("Tony Robbins", 0.3, "Self-help", "Media", "United States", "FL", "Palm Beach", 65, "Robbins Research"),
]

# ── CRYPTO / WEB3 ──
CRYPTO_WEALTHY = [
    ("Changpeng Zhao", 55.0, "Binance", "Cryptocurrency", "Canada", "", "Vancouver", 48, "Binance"),
    ("Sam Bankman-Fried", 8.0, "FTX", "Cryptocurrency", "United States", "CA", "Berkeley", 33, "FTX"),
    ("Brian Armstrong", 6.0, "Coinbase", "Cryptocurrency", "United States", "CA", "San Francisco", 42, "Coinbase"),
    ("Chris Larsen", 4.0, "Ripple", "Cryptocurrency", "United States", "CA", "San Francisco", 65, "Ripple Labs"),
    ("Brad Garlinghouse", 3.0, "Ripple", "Cryptocurrency", "United States", "CA", "San Francisco", 54, "Ripple Labs"),
    ("Vitalik Buterin", 6.5, "Ethereum", "Cryptocurrency", "Canada", "", "Toronto", 31, "Ethereum Foundation"),
    ("Barry Silbert", 5.0, "Digital Currency Group", "Cryptocurrency", "United States", "NY", "New York", 49, "DCG"),
    ("Cameron Winklevoss", 5.5, "Gemini", "Cryptocurrency", "United States", "NY", "New York", 43, "Gemini"),
    ("Tyler Winklevoss", 5.5, "Gemini", "Cryptocurrency", "United States", "NY", "New York", 43, "Gemini"),
    ("Michael Saylor", 2.0, "MicroStrategy", "Cryptocurrency", "United States", "VA", "Miami", 60, "MicroStrategy"),
    ("Anthony Pompliano", 0.5, "Morgan Creek", "Cryptocurrency", "United States", "NC", "Charlotte", 40, "Pomp Investments"),
    ("Tim Draper", 1.0, "VC, Bitcoin", "Cryptocurrency", "United States", "CA", "San Mateo", 67, "Draper Associates"),
    ("Marc Andreessen", 2.0, "VC, Crypto", "Technology", "United States", "CA", "Atherton", 53, "Andreessen Horowitz"),
]

# ── REAL ESTATE MOGULS ──
REAL_ESTATE = [
    ("Donald Trump", 3.0, "Real Estate, Media", "Real Estate", "United States", "FL", "Palm Beach", 78, "Trump Organization"),
    ("Stephen Ross", 10.0, "Related Companies", "Real Estate", "United States", "NY", "New York", 85, "Related Companies"),
    ("Sam Zell", 6.0, "Equity Residential", "Real Estate", "United States", "IL", "Chicago", 83, "Equity Group Investments"),
    ("Neil Bluhm", 4.0, "Real Estate", "Real Estate", "United States", "IL", "Chicago", 87, "JMB Realty"),
    ("Jeffrey Gundlach", 3.0, "DoubleLine Capital", "Finance", "United States", "CA", "Los Angeles", 66, "DoubleLine Capital"),
    ("Rick Caruso", 3.0, "Caruso Properties", "Real Estate", "United States", "CA", "Los Angeles", 66, "Caruso"),
    ("Harry Macklowe", 2.5, "Macklowe Properties", "Real Estate", "United States", "NY", "New York", 88, "Macklowe Properties"),
    ("Donald Bren", 18.0, "Irvine Company", "Real Estate", "United States", "CA", "Newport Beach", 93, "Irvine Company"),
    ("Edward Roski Jr", 4.0, "Majestic Realty", "Real Estate", "United States", "CA", "Los Angeles", 85, "Majestic Realty"),
    ("Irvine Company", 5.0, "Orange County RE", "Real Estate", "United States", "CA", "Newport Beach", 93, "Irvine Company"),
    ("Leonard Stern", 6.0, "Hartz Group", "Real Estate", "United States", "NY", "New York", 87, "Hartz Mountain"),
    ("Mortimer Zuckerman", 3.0, "Boston Properties", "Real Estate", "United States", "NY", "New York", 88, "Boston Properties"),
    ("Richard LeFrak", 4.0, "LeFrak Organization", "Real Estate", "United States", "NY", "New York", 79, "LeFrak"),
    ("Rob Speyer", 3.0, "Tishman Speyer", "Real Estate", "United States", "NY", "New York", 56, "Tishman Speyer"),
    ("Jerry Speyer", 4.0, "Tishman Speyer", "Real Estate", "United States", "NY", "New York", 85, "Tishman Speyer"),
]

# ── GENERATION POOLS ──

# Real company names for generation
COMPANIES = [
    "Apple", "Microsoft", "Amazon", "Alphabet", "Meta", "Tesla", "NVIDIA", "Berkshire Hathaway",
    "JPMorgan Chase", "Visa", "Mastercard", "Procter & Gamble", "Johnson & Johnson", "UnitedHealth",
    "Home Depot", "Verizon", "AT&T", "Comcast", "Pfizer", "AbbVie", "Merck", "Cisco", "Oracle",
    "PepsiCo", "Coca-Cola", "Starbucks", "McDonald's", "Nike", "Walmart", "Target", "Costco",
    "Lowe's", "Netflix", "Salesforce", "Adobe", "Intuit", "AMD", "Qualcomm", "Broadcom", "Texas Instruments",
    "Goldman Sachs", "Morgan Stanley", "BlackRock", "Blackstone", "KKR", "Apollo Global",
    "American Express", "Bank of America", "Citigroup", "Wells Fargo", "U.S. Bancorp",
    "ExxonMobil", "Chevron", "Shell", "BP", "TotalEnergies", "ConocoPhillips",
    "Boeing", "Lockheed Martin", "Raytheon", "Northrop Grumman", "General Dynamics",
    "General Electric", "Caterpillar", "Deere & Co", "3M", "Honeywell", "Union Pacific",
    "Danaher", "Thermo Fisher", "Abbott Labs", "Boston Scientific", "Medtronic", "Stryker",
    "FedEx", "UPS", "Delta Air Lines", "American Airlines", "Southwest Airlines",
    "Walt Disney", "Netflix", "Warner Bros Discovery", "Paramount Global", "Spotify",
    "Uber", "Lyft", "Airbnb", "DoorDash", "PayPal", "Square", "Shopify", "Twilio",
    "Snowflake", "Palantir", "CrowdStrike", "Zoom", "DocuSign", "Okta", "Datadog",
    "Coinbase", "Robinhood", "SoFi", "Chime", "Stripe", "Ripple", "Circle",
    "Moderna", "BioNTech", "Regeneron", "Gilead", "Amgen", "Biogen", "Vertex",
    "Samsung", "LG", "Hyundai", "Kia", "Sony", "Toyota", "Honda", "SoftBank",
    "Alibaba", "Tencent", "Baidu", "JD.com", "Meituan", "ByteDance", "Xiaomi",
    "Reliance Industries", "Tata Group", "Adani Group", "Infosys", "Wipro", "HCL",
    "LVMH", "L'Oreal", "Hermes", "Kering", "Chanel", "Richemont", "EssilorLuxottica",
    "Nestle", "Roche", "Novartis", "UBS", "Credit Suisse", "Zurich Insurance",
    "SAP", "Siemens", "Volkswagen", "BMW", "Mercedes-Benz", "Allianz", "Deutsche Telekom",
    "Shell", "BP", "GlaxoSmithKline", "AstraZeneca", "HSBC", "Unilever", "Diageo",
]

# Countries with wealth distribution weights
COUNTRIES = [
    ("United States", 0.35), ("China", 0.12), ("India", 0.08), ("Germany", 0.06),
    ("United Kingdom", 0.05), ("Switzerland", 0.04), ("Canada", 0.04), ("France", 0.04),
    ("Japan", 0.03), ("Australia", 0.03), ("Russia", 0.03), ("Brazil", 0.02),
    ("Hong Kong", 0.02), ("Singapore", 0.02), ("South Korea", 0.02), ("Sweden", 0.02),
    ("Netherlands", 0.02), ("Italy", 0.02), ("Spain", 0.01), ("UAE", 0.01),
    ("Saudi Arabia", 0.01), ("Taiwan", 0.01), ("Norway", 0.01), ("Denmark", 0.01),
    ("Israel", 0.01), ("Mexico", 0.01), ("Ireland", 0.01), ("South Africa", 0.01),
]

# US state distribution
US_STATES = [
    ("CA", 0.25), ("NY", 0.15), ("TX", 0.10), ("FL", 0.08), ("IL", 0.05),
    ("MA", 0.04), ("WA", 0.04), ("CT", 0.03), ("PA", 0.03), ("NJ", 0.03),
    ("GA", 0.02), ("CO", 0.02), ("MN", 0.02), ("OH", 0.02), ("VA", 0.02),
    ("NC", 0.02), ("MI", 0.02), ("OR", 0.01), ("AZ", 0.01), ("NV", 0.01),
]

US_CITIES = {
    "CA": ["San Francisco", "Los Angeles", "Palo Alto", "Atherton", "Woodside", "Hillsborough", "Newport Beach", "Irvine", "San Diego", "Menlo Park", "Cupertino", "Mountain View"],
    "NY": ["New York", "Manhattan", "Greenwich", "Scarsdale", "Bronxville", "Brooklyn"],
    "TX": ["Austin", "Dallas", "Houston", "Fort Worth", "San Antonio", "Frisco"],
    "FL": ["Miami", "Palm Beach", "Boca Raton", "Naples", "Orlando", "Tampa", "Jacksonville"],
    "IL": ["Chicago", "Evanston", "Lake Forest", "Winnetka", "Highland Park"],
    "MA": ["Boston", "Cambridge", "Newton", "Wellesley", "Lexington"],
    "WA": ["Seattle", "Bellevue", "Redmond", "Medina", "Hunts Point"],
    "CT": ["Greenwich", "Stamford", "New Canaan", "Darien", "Westport"],
    "PA": ["Philadelphia", "Pittsburgh", "Bryn Mawr", "Villanova"],
    "NJ": ["Princeton", "Short Hills", "Hoboken", "Jersey City"],
    "GA": ["Atlanta", "Alpharetta", "Milton", "Savannah", "Augusta"],
    "CO": ["Denver", "Boulder", "Aspen", "Vail", "Colorado Springs"],
    "MN": ["Minneapolis", "Saint Paul", "Wayzata", "Edina"],
    "OH": ["Columbus", "Cincinnati", "Cleveland", "Dayton", "Toledo"],
    "VA": ["McLean", "Arlington", "Alexandria", "Richmond"],
    "NC": ["Charlotte", "Raleigh", "Chapel Hill", "Durham", "Greensboro"],
    "MI": ["Detroit", "Grand Rapids", "Ann Arbor", "Birmingham"],
    "OR": ["Portland", "Beaverton", "Lake Oswego", "Salem"],
    "AZ": ["Phoenix", "Scottsdale", "Tucson", "Mesa", "Chandler"],
    "NV": ["Las Vegas", "Reno", "Henderson", "Incline Village"],
}

INTERNATIONAL_CITIES = {
    "United Kingdom": [("London", ""), ("Edinburgh", "Scotland"), ("Manchester", ""), ("Birmingham", ""), ("Cambridge", "")],
    "Canada": [("Toronto", "ON"), ("Vancouver", "BC"), ("Montreal", "QC"), ("Calgary", "AB"), ("Ottawa", "ON")],
    "Germany": [("Berlin", ""), ("Munich", ""), ("Hamburg", ""), ("Frankfurt", ""), ("Stuttgart", "")],
    "France": [("Paris", ""), ("Lyon", ""), ("Marseille", ""), ("Nice", ""), ("Bordeaux", "")],
    "Switzerland": [("Zurich", ""), ("Geneva", ""), ("Basel", ""), ("Bern", ""), ("Lugano", "")],
    "China": [("Beijing", ""), ("Shanghai", ""), ("Shenzhen", ""), ("Hangzhou", ""), ("Guangzhou", "")],
    "India": [("Mumbai", ""), ("New Delhi", ""), ("Bangalore", ""), ("Hyderabad", ""), ("Chennai", "")],
    "Japan": [("Tokyo", ""), ("Osaka", ""), ("Kyoto", ""), ("Yokohama", ""), ("Nagoya", "")],
    "Australia": [("Sydney", "NSW"), ("Melbourne", "VIC"), ("Brisbane", "QLD"), ("Perth", "WA"), ("Adelaide", "SA")],
    "Brazil": [("Sao Paulo", ""), ("Rio de Janeiro", ""), ("Brasilia", ""), ("Belo Horizonte", "")],
    "Russia": [("Moscow", ""), ("Saint Petersburg", ""), ("Novosibirsk", ""), ("Yekaterinburg", "")],
    "Singapore": [("Singapore", "")],
    "Hong Kong": [("Hong Kong", "")],
    "South Korea": [("Seoul", ""), ("Busan", ""), ("Incheon", "")],
    "Sweden": [("Stockholm", ""), ("Gothenburg", ""), ("Malmo", "")],
    "Netherlands": [("Amsterdam", ""), ("Rotterdam", ""), ("The Hague", ""), ("Utrecht", "")],
    "Italy": [("Milan", ""), ("Rome", ""), ("Florence", ""), ("Turin", "")],
    "Spain": [("Madrid", ""), ("Barcelona", ""), ("Valencia", ""), ("Seville", "")],
    "UAE": [("Dubai", ""), ("Abu Dhabi", "")],
    "Saudi Arabia": [("Riyadh", ""), ("Jeddah", ""), ("Mecca", "")],
    "Taiwan": [("Taipei", ""), ("Kaohsiung", "")],
    "Norway": [("Oslo", ""), ("Bergen", "")],
    "Denmark": [("Copenhagen", ""), ("Aarhus", "")],
    "Israel": [("Tel Aviv", ""), ("Jerusalem", ""), ("Haifa", "")],
    "Mexico": [("Mexico City", ""), ("Monterrey", ""), ("Guadalajara", "")],
    "Ireland": [("Dublin", ""), ("Cork", "")],
    "South Africa": [("Johannesburg", ""), ("Cape Town", ""), ("Durban", "")],
    "Portugal": [("Lisbon", ""), ("Porto", "")],
    "Argentina": [("Buenos Aires", ""), ("Cordoba", ""), ("Rosario", "")],
    "Turkey": [("Istanbul", ""), ("Ankara", "")],
}

INDUSTRIES = [
    "Technology", "Finance", "Healthcare", "Energy", "Consumer Goods", "Fashion & Retail",
    "Real Estate", "Media", "Entertainment", "Telecommunications", "Manufacturing",
    "Automotive", "Aerospace", "Pharmaceuticals", "Biotechnology", "Insurance",
    "Mining", "Steel", "Chemicals", "Agriculture", "Food & Beverage", "Hospitality",
    "Transportation", "Logistics", "Cryptocurrency", "Gaming", "Sports", "Education",
    "Diversified", "Private Equity", "Venture Capital", "Hedge Fund",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna",
    "Kenneth", "Michelle", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Frank", "Christine", "Gregory", "Debra",
    "Raymond", "Rachel", "Patrick", "Carolyn", "Jack", "Janet", "Dennis", "Catherine",
    "Jerry", "Maria", "Alexander", "Heather", "Peter", "Diane", "Harold", "Ruth",
    "William", "Olivia", "Liam", "Sophia", "Noah", "Charlotte", "Oliver", "Mia",
    "Henry", "Evelyn", "Sebastian", "Abigail", "Jack", "Harper", "Owen", "Aria",
    "Theodore", "Grace", "Aiden", "Chloe", "Samuel", "Ella", "Joseph", "Avery",
    "Levi", "Scarlett", "Mateo", "Victoria", "David", "Madison", "John", "Luna",
    "Wyatt", "Camila", "Carter", "Penelope", "Julian", "Layla", "Luke", "Riley",
    "Grayson", "Zoey", "Isaac", "Nora", "Jayden", "Lily", "Gabriel", "Eleanor",
    "Anthony", "Hannah", "Dylan", "Lillian", "Leo", "Addison", "Lincoln", "Aubrey",
    "Jaxon", "Ellie", "Asher", "Stella", "Christopher", "Natalie", "Josiah", "Willow",
    "Andrew", "Leah", "Thomas", "Hazel", "Charles", "Violet", "Caleb", "Aurora",
    "Ethan", "Savannah", "Aaron", "Audrey", "Nathan", "Brooklyn", "Isaiah", "Bella",
    "Ryan", "Claire", "Mason", "Skylar", "Eli", "Lucy", "Landon", "Paisley",
    "Christian", "Everly", "Hunter", "Anna", "Connor", "Caroline", "Adrian", "Nova",
    "James", "Genesis", "Axel", "Emilia", "Wesley", "Kennedy", "Roman", "Sienna",
    "Luca", "Maya", "Xavier", "Sara", "Bryce", "Valentina", "Jasper", "Rylee",
    "Kayden", "Naomi", "Silas", "Alice", "Ezra", "Kehlani", "Ian", "Ruth",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward",
    "Richardson", "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray",
    "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel",
    "Myers", "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry",
    "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Coleman",
    "Gonzales", "Fisher", "Yang", "MacDonald", "Chan", "Gupta", "Sharma", "Patel",
    "Singh", "Kumar", "Desai", "Shah", "Joshi", "Mehta", "Agarwal", "Rao",
    "Reddy", "Nair", "Menon", "Iyer", "Mishra", "Dubey", "Tiwari", "Pandey",
    "Johansson", "Andersson", "Nilsson", "Karlsson", "Eriksson", "Larsson", "Svensson",
    "Muller", "Schmidt", "Schneider", "Fischer", "Weber", "Wagner", "Becker", "Hoffmann",
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci",
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Wu", "Zhou", "Xu",
    "Kim", "Park", "Choi", "Lee", "Jung", "Kang", "Cho", "Yoon", "Jang", "Lim",
    "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura",
    "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki", "Yamaguchi", "Matsumoto",
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Ferreira",
    "Almeida", "Rodrigues", "Nunes", "Carvalho", "Gomes", "Martins", "Barbosa",
    "Okafor", "Osei", "Nkosi", "Mensah", "Adebayo", "Kamara", "Diallo", "Traore",
    "Ahmed", "Ali", "Hassan", "Hussein", "Mohamed", "Abdullah", "Omar", "Saleh",
]

# Net worth distribution by tier (in billions)
TIER_RANGES = {
    "billionaire": (1.0, 200.0),
    "centi-millionaire": (0.1, 0.999),
    "multi-millionaire": (0.01, 0.099),
    "millionaire": (0.001, 0.0099),
}

TIER_DISTRIBUTION = [
    ("millionaire", 0.50),
    ("multi-millionaire", 0.30),
    ("centi-millionaire", 0.15),
    ("billionaire", 0.05),
]

def pick_weighted(items):
    total = sum(w for _, w in items)
    r = random.random() * total
    cum = 0
    for item, w in items:
        cum += w
        if r <= cum:
            return item
    return items[-1][0]

def generate_net_worth(tier):
    lo, hi = TIER_RANGES[tier]
    if tier == "billionaire":
        return round(random.uniform(lo, min(hi, 100.0)) ** 1.5 / 100.0 ** 0.5, 3)
    return round(random.uniform(lo, hi), 4)

def get_location(country):
    if country == "United States":
        state = pick_weighted(US_STATES)
        city = random.choice(US_CITIES.get(state, ["Unknown"]))
        return country, state, city
    elif country in INTERNATIONAL_CITIES:
        city, state = random.choice(INTERNATIONAL_CITIES[country])
        return country, state, city
    else:
        return country, "", ""

def make_country_tiers(country):
    """Generate appropriate tier distribution per country."""
    if country == "United States":
        return TIER_DISTRIBUTION
    elif country in ("China", "India", "Germany", "United Kingdom"):
        return [("millionaire", 0.45), ("multi-millionaire", 0.30), ("centi-millionaire", 0.15), ("billionaire", 0.10)]
    elif country in ("Switzerland", "Canada", "France", "Japan", "Australia", "Russia", "Hong Kong", "Singapore"):
        return [("millionaire", 0.50), ("multi-millionaire", 0.30), ("centi-millionaire", 0.12), ("billionaire", 0.08)]
    else:
        return [("millionaire", 0.55), ("multi-millionaire", 0.30), ("centi-millionaire", 0.10), ("billionaire", 0.05)]

def gather_real_contacts():
    """Gather all hardcoded real contacts."""
    contacts = []
    
    for name, nw, src, ind, country, state, city, age, company in BILLIONAIRES:
        contacts.append({
            "name": name, "net_worth": nw, "source": src, "industry": ind,
            "country": country, "state": state, "city": city, "age": age,
            "company": company, "wealth_tier": "billionaire"
        })
    
    already = {(c["name"], c["country"]): True for c in contacts}
    
    for name, nw, src, ind, country, state, city, age, company in EXECUTIVES:
        key = (name, country)
        if key not in already:
            tier = "billionaire" if nw >= 1.0 else ("centi-millionaire" if nw >= 0.1 else "millionaire")
            contacts.append({
                "name": name, "net_worth": nw, "source": src, "industry": ind,
                "country": country, "state": state, "city": city, "age": age,
                "company": company, "wealth_tier": tier
            })
            already[key] = True
    
    for name, nw, src, ind, country, state, city, age, company in SPORTS + ENTERTAINERS + CRYPTO_WEALTHY + REAL_ESTATE:
        key = (name, country)
        if key not in already:
            tier = "billionaire" if nw >= 1.0 else ("centi-millionaire" if nw >= 0.1 else "millionaire")
            contacts.append({
                "name": name, "net_worth": nw, "source": src, "industry": ind,
                "country": country, "state": state, "city": city, "age": age,
                "company": company, "wealth_tier": tier
            })
            already[key] = True
    
    return contacts

def generate_contacts(target_total=5000):
    """Generate contacts to reach target_total, combining real + synthetic."""
    random.seed(42)
    
    real_contacts = gather_real_contacts()
    all_contacts = list(real_contacts)
    existing = {(c["name"], c["country"]): True for c in all_contacts}
    
    need = target_total - len(all_contacts)
    if need <= 0:
        return all_contacts
    
    name_pool = [(f, l) for f in FIRST_NAMES for l in LAST_NAMES]
    random.shuffle(name_pool)
    name_idx = 0
    
    for i in range(need):
        if name_idx >= len(name_pool):
            break
        
        first, last = name_pool[name_idx]
        name_idx += 1
        full_name = f"{first} {last}"
        
        country = pick_weighted(COUNTRIES)
        ctry, state, city = get_location(country)
        
        key = (full_name, ctry)
        if key in existing:
            continue
        existing[key] = True
        
        tiers = make_country_tiers(ctry)
        tier = pick_weighted(tiers)
        nw = generate_net_worth(tier)
        
        company = random.choice(COMPANIES)
        industry = random.choice(INDUSTRIES)
        source = f"{industry}/{tier}"
        age = random.randint(25, 85)
        
        all_contacts.append({
            "name": full_name, "net_worth": nw, "source": source, "industry": industry,
            "country": ctry, "state": state, "city": city, "age": age,
            "company": company, "wealth_tier": tier
        })
    
    random.shuffle(all_contacts)
    for i, c in enumerate(all_contacts, 1):
        c["rank"] = i
    
    return all_contacts

if __name__ == "__main__":
    contacts = generate_contacts(5000)
    print(f"Generated {len(contacts)} contacts")
    tiers = {}
    for c in contacts:
        tiers[c["wealth_tier"]] = tiers.get(c["wealth_tier"], 0) + 1
    print("By tier:", tiers)
    
    countries = {}
    for c in contacts:
        countries[c["country"]] = countries.get(c["country"], 0) + 1
    print("Top countries:", sorted(countries.items(), key=lambda x: -x[1])[:10])
