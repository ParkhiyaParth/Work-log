# Expiry Reminder
Installable PWA for an off-licence: scan a product's QR code, save its expiry date, and get an end-of-day list of stock to pull.

Run: `python3 -m http.server 8000` in this folder, open on the phone (camera needs HTTPS or localhost; GitHub Pages works), then "Add to Home Screen".

## Using it
- **Scan** (any barcode or QR) opens the product. Known product: all its stock batches with quantity and expiry, expired/today in red. New product: enter the name.
- **Add stock**: quantity, expiry date from the calendar (or +1 week / month / year buttons), then Add stock. Each batch keeps its own date.
- **+ New product** on the Products tab adds a product by hand; the barcode is optional.
- A reminder fires at the end-of-day time (Settings) on the day a batch expires.
- QR codes carrying data (JSON, URL params, GS1 `(17)` expiry, `key: value`) prefill name/expiry; plain barcodes just match the product.

## Android app
`.github/workflows/android-expiry.yml` builds `ExpiryReminder.apk` (Capacitor) on every push touching this folder, or via
Actions > "Build Expiry Reminder APK" > Run workflow, and attaches it to a GitHub release (`expiry-apk-N`).
Install it on the phone (allow "install unknown apps"), then allow camera and notifications when asked.

In the app, one notification per expiry day is scheduled with Android's alarm system at the end-of-day time from
Settings (default 20:00) listing the products that expire that day. It fires even when the app is closed, and is
rescheduled whenever stock changes. In a normal browser (PWA) it only fires while the app is open.

Parser tests: `node test-parser.js`
