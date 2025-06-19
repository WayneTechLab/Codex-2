# Codex-2

This repository now contains a small Flask application that displays crypto news from several RSS feeds. The app offers a home page, about page, contact page and a news page where you can filter by crypto category and news source.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the web app:

```bash
python app.py
```

Then open `http://localhost:5000` in your browser. If a feed cannot be retrieved (for example due to network restrictions), the app prints a warning and continues.

You can still run the original command-line script to fetch Bitcoin headlines:

```bash
python bitcoin_news.py --limit 5
```
