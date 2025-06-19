import feedparser
import argparse
from datetime import datetime, timezone

DEFAULT_FEEDS = [
    'https://news.bitcoin.com/feed/',
    'https://cointelegraph.com/rss',
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
]


def parse_args():
    parser = argparse.ArgumentParser(description='Show latest Bitcoin news from various RSS feeds')
    parser.add_argument('--feeds', nargs='+', help='List of RSS feed URLs to parse', default=DEFAULT_FEEDS)
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of headlines to display')
    return parser.parse_args()


def fetch_entries(feed_url):
    parsed = feedparser.parse(feed_url)
    entries = parsed.entries
    return entries


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
    all_entries = []
    for feed_url in args.feeds:
        entries = fetch_entries(feed_url)
        all_entries.extend(filter_bitcoin_entries(entries))
    # Sort by timestamp descending
    all_entries.sort(key=lambda x: x[0], reverse=True)
    for timestamp, entry in all_entries[: args.limit]:
        title = entry.get('title')
        link = entry.get('link')
        published = timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')
        print(f"{published} - {title}\n{link}\n")


if __name__ == '__main__':
    main()
