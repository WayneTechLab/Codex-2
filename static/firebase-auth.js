import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, doc, setDoc, getDoc, collection, addDoc, getDocs } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCtH1aD4o7UrVurErsHUu9ZIJzXsZWBYwE",
  authDomain: "coinpro-cc.firebaseapp.com",
  projectId: "coinpro-cc",
  storageBucket: "coinpro-cc.appspot.com",
  messagingSenderId: "649941850095",
  appId: "1:649941850095:web:7d73d1cdaea366b513481a",
  measurementId: "G-S801QZ4SLZ"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const db = getFirestore(app);

const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const profileInfo = document.getElementById('profile-info');
const loginSection = document.getElementById('login-section');
const profileName = document.getElementById('profile-name');
const profileEmail = document.getElementById('profile-email');
const favoritesList = document.getElementById('favorites-list');
const welcomeOverlay = document.getElementById('welcome-overlay');
const welcomeLoginBtn = document.getElementById('welcome-login-btn');

// Save a bookmark
async function addBookmark(user, entry) {
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    let bookmarks = [];
    if (userSnap.exists() && userSnap.data().bookmarks) {
        bookmarks = userSnap.data().bookmarks;
    }
    // Avoid duplicates
    if (!bookmarks.some(b => b.link === entry.link)) {
        bookmarks.push(entry);
        await setDoc(userRef, { bookmarks }, { merge: true });
        // REMOVE: loadBookmarks(user);
    }
}

// Remove a bookmark
async function removeBookmark(user, entry) {
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    let bookmarks = [];
    if (userSnap.exists() && userSnap.data().bookmarks) {
        bookmarks = userSnap.data().bookmarks.filter(b => b.link !== entry.link);
        await setDoc(userRef, { bookmarks }, { merge: true });
        // REMOVE: loadBookmarks(user);
    }
}

// Load bookmarks and display
async function loadBookmarks(user) {
    if (!favoritesList) return;
    favoritesList.innerHTML = '';
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    let bookmarks = [];
    if (userSnap.exists() && userSnap.data().bookmarks) {
        bookmarks = userSnap.data().bookmarks;
    }
    if (bookmarks.length === 0) {
        favoritesList.innerHTML = '<li>No bookmarks yet.</li>';
        return;
    }
    bookmarks.forEach(entry => {
        const li = document.createElement('li');
        const star = document.createElement('span');
        star.className = 'bookmark bookmarked';
        star.title = 'Remove Bookmark';
        star.innerHTML = '&#9733;';
        star.onclick = () => removeBookmark(auth.currentUser, entry);
        li.appendChild(star);

        const a = document.createElement('a');
        a.href = entry.link;
        a.target = '_blank';
        a.textContent = entry.title;
        li.appendChild(a);

        const small = document.createElement('small');
        small.textContent = ` (${entry.published}) - ${entry.source}`;
        li.appendChild(small);

        favoritesList.appendChild(li);
    });
}

// Update on auth state
onAuthStateChanged(auth, user => {
    if (user) {
        // Hide welcome overlay if present
        if (welcomeOverlay) welcomeOverlay.style.display = 'none';
        // Optionally redirect to home or profile
        // window.location.href = '/';
        if (profileInfo) profileInfo.style.display = '';
        if (loginSection) loginSection.style.display = 'none';
        if (profileName) profileName.textContent = user.displayName;
        if (profileEmail) profileEmail.textContent = user.email;
        if (typeof loadBookmarks === "function") loadBookmarks(user);
        markBookmarkedNews(user);
    } else {
        if (welcomeOverlay) welcomeOverlay.style.display = 'flex';
        if (profileInfo) profileInfo.style.display = 'none';
        if (loginSection) loginSection.style.display = '';
        if (profileName) profileName.textContent = '';
        if (profileEmail) profileEmail.textContent = '';
        if (favoritesList) favoritesList.innerHTML = '';
    }
});

// --- Bookmark toggle for news lists ---
function setupBookmarkToggles() {
    document.querySelectorAll('.news-list .bookmark').forEach(star => {
        star.onclick = async function () {
            if (!auth.currentUser) {
                showToast('Please login to bookmark news.', true);
                return;
            }
            const li = this.closest('li');
            const a = li.querySelector('a');
            const small = li.querySelector('small');
            const entry = {
                title: a.textContent,
                link: a.href,
                published: small.textContent.match(/\((.*?)\)/)?.[1] || "",
                source: small.textContent.split('-').pop().trim()
            };
            try {
                if (this.classList.contains('bookmarked')) {
                    await removeBookmark(auth.currentUser, entry);
                    this.classList.remove('bookmarked');
                    this.innerHTML = '&#9734;';
                    showToast('Bookmark removed.');
                } else {
                    await addBookmark(auth.currentUser, entry);
                    this.classList.add('bookmarked');
                    this.innerHTML = '&#9733;';
                    showToast('Bookmarked!');
                }
            } catch (err) {
                showToast('Error updating bookmark.', true);
                console.error(err);
            }
        };
    });
}

// Mark bookmarked news on load
async function markBookmarkedNews(user) {
    if (!user) return;
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    let bookmarks = [];
    if (userSnap.exists() && userSnap.data().bookmarks) {
        bookmarks = userSnap.data().bookmarks;
    }
    document.querySelectorAll('.news-list li').forEach(li => {
        const a = li.querySelector('a');
        const star = li.querySelector('.bookmark');
        if (!a || !star) return;
        const isBookmarked = bookmarks.some(b => b.link === a.href);
        if (isBookmarked) {
            star.classList.add('bookmarked');
            star.innerHTML = '&#9733;';
        } else {
            star.classList.remove('bookmarked');
            star.innerHTML = '&#9734;';
        }
    });
}

onAuthStateChanged(auth, user => {
    if (user) {
        // Hide welcome overlay if present
        if (welcomeOverlay) welcomeOverlay.style.display = 'none';
        // Optionally redirect to home or profile
        // window.location.href = '/';
        if (profileInfo) profileInfo.style.display = '';
        if (loginSection) loginSection.style.display = 'none';
        if (profileName) profileName.textContent = user.displayName;
        if (profileEmail) profileEmail.textContent = user.email;
        if (typeof loadBookmarks === "function") loadBookmarks(user);
        markBookmarkedNews(user);
    } else {
        if (welcomeOverlay) welcomeOverlay.style.display = 'flex';
        if (profileInfo) profileInfo.style.display = 'none';
        if (loginSection) loginSection.style.display = '';
        if (profileName) profileName.textContent = '';
        if (profileEmail) profileEmail.textContent = '';
        if (favoritesList) favoritesList.innerHTML = '';
    }
});

// Toast notification function
function showToast(msg, isError = false) {
    let toast = document.getElementById('bookmark-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'bookmark-toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '30px';
        toast.style.right = '30px';
        toast.style.background = isError ? '#e74c3c' : '#23272f';
        toast.style.color = '#fff';
        toast.style.padding = '14px 24px';
        toast.style.borderRadius = '8px';
        toast.style.fontSize = '1.1em';
        toast.style.zIndex = 9999;
        toast.style.boxShadow = '0 2px 12px #0008';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = 1;
    setTimeout(() => { toast.style.opacity = 0; }, 1800);
}

// Save news to Firestore
async function save_news_to_firestore(news_item) {
    const db = getFirestore();
    const newsRef = doc(db, "news", safeDocId(news_item.link));  // Use link as unique ID
    await setDoc(newsRef, news_item);
}

// Get news from Firestore
async function get_news_from_firestore() {
    const db = getFirestore();
    const newsCollection = collection(db, "news");
    const newsSnapshot = await getDocs(newsCollection);
    return newsSnapshot.docs.map(doc => doc.data());
}

// Safe document ID function
function safeDocId(url) {
    return btoa(url).replace(/\//g, '_');
}

// Run on page load
window.addEventListener('DOMContentLoaded', () => {
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) {
        loginBtn.onclick = () => signInWithPopup(auth, provider)
            .catch(err => {
                alert("Login failed: " + err.message);
                console.error(err);
            });
    }
    if (logoutBtn) {
        logoutBtn.onclick = () => signOut(auth);
    }
    setupBookmarkToggles();

    // Firestore operations
    const db = getFirestore();
    // Example: Add a news item
    const newsItem = {
        title: "Sample News",
        link: "https://example.com/sample-news",
        published: new Date().toISOString(),
        source: "Example News Source"
    };
    save_news_to_firestore(newsItem)
        .then(() => console.log("News saved to Firestore"))
        .catch(err => console.error("Error saving news to Firestore:", err));
});

// Remove any broken CSS-in-JS or stray code blocks at the end of this file.

if (typeof window !== "undefined") {
    window.addEventListener('load', function () {
        // Your code to run after the window has loaded
    });
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        addBookmark,
        removeBookmark,
        loadBookmarks,
        markBookmarkedNews,
        showToast,
        save_news_to_firestore,
        get_news_from_firestore
    };
}

if (typeof process !== "undefined" && process.versions && process.versions.node) {
    // Node.js specific code
    const http = require('http');
    const port = process.env.PORT || 5000;

    const server = http.createServer((req, res) => {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('Server is running\n');
    });

    server.listen(port, () => {
        console.log(`Server running at http://localhost:${port}/`);
    });
}