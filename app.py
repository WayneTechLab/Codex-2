from flask import Flask, render_template, request
import feedparser
from datetime import datetime, timezone
import sqlite3
import requests

app = Flask(__name__)

DB_PATH = 'news.db'


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            source TEXT,
            published TEXT,
            summary TEXT
        )"""
    )
    con.commit()
    con.close()


def save_entry(entry, source_name):
    """Insert news entry into database if not already present."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT OR IGNORE INTO news (title, link, source, published, summary) VALUES (?, ?, ?, ?, ?)",
            (
                entry.get('title'),
                entry.get('link'),
                source_name,
                entry.get('published'),
                entry.get('summary', '')
            ),
        )
        con.commit()
    finally:
        con.close()


def get_crypto_ticker():
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [
                {"symbol": item["symbol"].upper(), "price": f"{item['current_price']:.2f}"}
                for item in data
            ]
    except Exception as exc:
        print(f"Warning: could not fetch ticker: {exc}")
    return []


@app.context_processor
def inject_ticker():
    return {"ticker": get_crypto_ticker()}


init_db()


def query_archive(year=None, month=None, day=None, ampm=None, limit=100):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    query = "SELECT title, link, source, published, summary FROM news"
    conditions = []
    params = []
    if year:
        conditions.append("strftime('%Y', published)=?")
        params.append(str(year))
    if month:
        conditions.append("strftime('%m', published)=?")
        params.append(str(month).zfill(2))
    if day:
        conditions.append("strftime('%d', published)=?")
        params.append(str(day).zfill(2))
    if ampm:
        if ampm == 'AM':
            conditions.append("CAST(strftime('%H', published) AS INTEGER) < 12")
        else:
            conditions.append("CAST(strftime('%H', published) AS INTEGER) >= 12")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY datetime(published) DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    rows = cur.fetchall()
    con.close()
    result = []
    for row in rows:
        result.append({
            'title': row[0],
            'link': row[1],
            'source': row[2],
            'published': row[3]
        })
    return result

FEEDS = {
    'Bitcoin.com': 'https://news.bitcoin.com/feed/',
    'CoinTelegraph': 'https://cointelegraph.com/rss',
    'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/'
}

CATEGORIES = [
    'Bitcoin', 'Blockchain', 'Ethereum', 'Litecoin', 'Ripple',
    'Cardano', 'Dogecoin', 'Solana', 'Polygon', 'Polkadot',
    'Chainlink', 'Binance'
]


def fetch_entries(url):
    try:
        parsed = feedparser.parse(url)
        if parsed.bozo:
            raise parsed.bozo_exception
        return parsed.entries
    except Exception as exc:
        print(f"Warning: could not retrieve {url}: {exc}")
        return []


def filter_entries(entries, keyword=None):
    filtered = []
    for e in entries:
        title = e.get('title', '')
        summary = e.get('summary', '')
        if not keyword or keyword.lower() in title.lower() or keyword.lower() in summary.lower():
            published = e.get('published_parsed')
            if published:
                timestamp = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)
            filtered.append((timestamp, e))
    return filtered


def get_news(category=None, source=None, limit=10):
    feeds = FEEDS
    if source and source in FEEDS:
        feeds = {source: FEEDS[source]}
    all_entries = []
    keyword = category if category and category != 'All' else None
    for name, url in feeds.items():
        entries = fetch_entries(url)
        filtered = filter_entries(entries, keyword)
        for ts, entry in filtered:
            entry['source'] = name
            save_entry(entry, name)
        all_entries.extend(filtered)
    all_entries.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in all_entries[:limit]]


@app.route('/')
def home():
    news = get_news(limit=10)
    return render_template('home.html', news=news)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/news')
def news():
    category = request.args.get('category', 'All')
    source = request.args.get('source', 'All')
    selected_category = category
    selected_source = source
    if category == 'All':
        category = None
    if source == 'All':
        source = None
    news = get_news(category=category, source=source, limit=10)
    return render_template(
        'news.html',
        news=news,
        categories=['All'] + CATEGORIES,
        sources=['All'] + list(FEEDS.keys()),
        selected_category=selected_category,
        selected_source=selected_source,
    )


@app.route('/archive')
def archive():
    year = request.args.get('year') or None
    month = request.args.get('month') or None
    day = request.args.get('day') or None
    ampm = request.args.get('ampm') or None
    news = query_archive(year, month, day, ampm)
    # Build filter options
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT strftime('%Y', published) FROM news ORDER BY 1 DESC")
    years = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT strftime('%m', published) FROM news ORDER BY 1")
    months = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT strftime('%d', published) FROM news ORDER BY 1")
    days = [r[0] for r in cur.fetchall()]
    con.close()
    return render_template(
        'archive.html',
        news=news,
        years=years,
        months=months,
        days=days,
        selected_year=year,
        selected_month=month,
        selected_day=day,
        selected_ampm=ampm,
    )


@app.route('/profile')
def profile():
    return render_template('profile.html', ticker=get_ticker_data())


def get_ticker_data():
    # Example static data; replace with your real ticker logic if needed
    return [
        {"symbol": "BTC", "price": "65000"},
        {"symbol": "ETH", "price": "3500"}
    ]


@app.route('/favorites')
def favorites():
    return render_template('favorites.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
