const express = require('express');
const path = require('path');
const Parser = require('rss-parser');
const ejsLayouts = require('express-ejs-layouts');

const app = express();
const parser = new Parser();

const FEEDS = {
  'Bitcoin.com': 'https://news.bitcoin.com/feed/',
  'CoinTelegraph': 'https://cointelegraph.com/rss',
  'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/'
};

const CATEGORIES = [
  'Bitcoin', 'Blockchain', 'Ethereum', 'Litecoin', 'Ripple',
  'Cardano', 'Dogecoin', 'Solana', 'Polygon', 'Polkadot',
  'Chainlink', 'Binance'
];

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('layout', 'base');
app.use(ejsLayouts);
app.use('/static', express.static(path.join(__dirname, 'static')));

async function fetchEntries(url) {
  try {
    return await parser.parseURL(url).then(feed => feed.items);
  } catch (err) {
    console.warn(`Warning: could not retrieve ${url}: ${err.message}`);
    return [];
  }
}

function filterEntries(entries, keyword) {
  return entries.filter(e => {
    if (!keyword) return true;
    const title = e.title || '';
    const summary = e.contentSnippet || '';
    return title.toLowerCase().includes(keyword.toLowerCase()) ||
           summary.toLowerCase().includes(keyword.toLowerCase());
  }).map(e => {
    e.published = e.isoDate || e.pubDate || new Date().toISOString();
    return e;
  });
}

async function getNews(category, source, limit = 10) {
  let feeds = FEEDS;
  if (source && FEEDS[source]) {
    feeds = { [source]: FEEDS[source] };
  }
  const keyword = category && category !== 'All' ? category : null;
  let allEntries = [];
  for (const url of Object.values(feeds)) {
    const entries = await fetchEntries(url);
    allEntries = allEntries.concat(filterEntries(entries, keyword));
  }
  allEntries.sort((a, b) => new Date(b.published) - new Date(a.published));
  return allEntries.slice(0, limit);
}

app.get('/', async (req, res) => {
  const news = await getNews(null, null, 10);
  res.render('home', { news });
});

app.get('/about', (req, res) => {
  res.render('about');
});

app.get('/contact', (req, res) => {
  res.render('contact');
});

app.get('/news', async (req, res) => {
  const category = req.query.category || 'All';
  const source = req.query.source || 'All';
  const news = await getNews(
    category === 'All' ? null : category,
    source === 'All' ? null : source,
    10
  );
  res.render('news', {
    news,
    categories: ['All', ...CATEGORIES],
    sources: ['All', ...Object.keys(FEEDS)],
    selected_category: category,
    selected_source: source
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
