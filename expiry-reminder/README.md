# Expiry Reminder
Installable PWA for an off-licence: scan a product's QR code, save its expiry date, and get an end-of-day list of stock to pull.

Run: `python3 -m http.server 8000` in this folder, open on the phone (camera needs HTTPS or localhost; GitHub Pages works), then "Add to Home Screen".

## QR formats understood
JSON (`{"name":"..","expiry":"31/12/2026"}`), URLs with `?name=&exp=`, GS1 codes (`(01)…(17)YYMMDD(10)batch`),
`key: value` text, or any text containing a date. If the QR has no expiry date you type it in after scanning.
Dates are read UK-style (day/month/year).

## Reminders
At the time set in Settings (default 20:00) the app shows/notifies what is expired or expiring today. Browsers cannot
wake a closed PWA, so this fires when the app is open or next opened after that time. For true background alerts,
wrap it with Capacitor + Local Notifications (as the Work Log app does for its APK).

Parser tests: `node test-parser.js`
