# Codex-2

This repository now contains a Flask application that displays crypto news from several RSS feeds. Headlines are stored in a small SQLite database so you can browse an archive of past stories. The interface includes a hacker-style dark theme and a live ticker of the top 10 cryptocurrencies.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the web app:

```bash
python app.py
```

Then open `http://localhost:5000` in your browser. If a feed cannot be retrieved (for example due to network restrictions), the app prints a warning and continues. News items are saved to `news.db` so they can be browsed later on the **Archive** page.

You can still run the original command-line script to fetch Bitcoin headlines:

```bash
python bitcoin_news.py --limit 5
```
