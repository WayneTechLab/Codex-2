from flask import Flask, render_template, request
import feedparser
from datetime import datetime, timezone

app = Flask(__name__)

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
    for url in feeds.values():
        entries = fetch_entries(url)
        all_entries.extend(filter_entries(entries, keyword))
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
