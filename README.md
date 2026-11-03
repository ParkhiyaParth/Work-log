# Work Log
Personal mobile work-hours & payout tracker (installable PWA, works offline, data stays on your device).

Run: `python3 -m http.server 8000` and open on your phone (same Wi-Fi), or host the folder on any static host (GitHub Pages),
then "Add to Home Screen".

## Going live
Pushing to `main` deploys the app to GitHub Pages via `.github/workflows/pages.yml`
(URL: `https://<your-username>.github.io/Work-log/`). Everyone who opens the link gets their own private copy;
hours are stored on each person's own phone.
