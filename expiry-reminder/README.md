# Expiry Reminder
Installable PWA for an off-licence: scan a product's QR code, save its expiry date, and get an end-of-day list of stock to pull.

Run: `python3 -m http.server 8000` in this folder, open on the phone (camera needs HTTPS or localhost; GitHub Pages works), then "Add to Home Screen".

## QR formats understood
JSON (`{"name":"..","expiry":"31/12/2026"}`), URLs with `?name=&exp=`, GS1 codes (`(01)…(17)YYMMDD(10)batch`),
`key: value` text, or any text containing a date. If the QR has no expiry date you type it in after scanning.
Dates are read UK-style (day/month/year).

## Android app
`.github/workflows/android-expiry.yml` builds `ExpiryReminder.apk` (Capacitor) on every push touching this folder, or via
Actions > "Build Expiry Reminder APK" > Run workflow, and attaches it to a GitHub release (`expiry-apk-N`).
Install it on the phone (allow "install unknown apps"), then allow camera and notifications when asked.

In the app, one notification per expiry day is scheduled with Android's alarm system at the end-of-day time from
Settings (default 20:00) listing the products that expire that day. It fires even when the app is closed, and is
rescheduled whenever stock changes. In a normal browser (PWA) it only fires while the app is open.

Parser tests: `node test-parser.js`
