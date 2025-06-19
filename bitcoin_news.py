import feedparser
import argparse
from datetime import datetime, timezone
import sqlite3

DEFAULT_FEEDS = [
    'https://news.bitcoin.com/feed/',
    'https://cointelegraph.com/rss',
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
]

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


def parse_args():
    parser = argparse.ArgumentParser(description='Show latest Bitcoin news from various RSS feeds')
    parser.add_argument('--feeds', nargs='+', help='List of RSS feed URLs to parse', default=DEFAULT_FEEDS)
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of headlines to display')
    return parser.parse_args()


def fetch_entries(feed_url):
    """Return list of entries for the given RSS feed URL."""
    try:
        parsed = feedparser.parse(feed_url)
        if parsed.bozo:
            raise parsed.bozo_exception
        return parsed.entries
    except Exception as exc:
        print(f"Warning: could not retrieve {feed_url}: {exc}")
        return []


def filter_bitcoin_entries(entries):
    filtered = []
    for entry in entries:
        title = entry.get('title', '')
        summary = entry.get('summary', '')
        if 'bitcoin' in title.lower() or 'bitcoin' in summary.lower() or 'btc' in title.lower():
            published = entry.get('published_parsed')
            if published:
                timestamp = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)
            filtered.append((timestamp, entry))
    return filtered


def main():
    args = parse_args()
    init_db()
    all_entries = []
    for feed_url in args.feeds:
        entries = fetch_entries(feed_url)
        filtered = filter_bitcoin_entries(entries)
        for ts, entry in filtered:
            save_entry(entry, feed_url)
        all_entries.extend(filtered)
    # Sort by timestamp descending
    all_entries.sort(key=lambda x: x[0], reverse=True)
    if not all_entries:
        print("No entries fetched. Check your network connection or feed URLs.")
        return
    for timestamp, entry in all_entries[: args.limit]:
        title = entry.get('title')
        link = entry.get('link')
        published = timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')
        print(f"{published} - {title}\n{link}\n")


if __name__ == '__main__':
    main()
