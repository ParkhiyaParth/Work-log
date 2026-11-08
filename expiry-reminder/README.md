# Expiry Reminder

Mobile app (Expo / React Native). Add a product name and expiry date; at 21:00 on that date you get a notification: "Remove <product> from the shelf."

## Run on your phone
1. Install **Expo Go** from the Play Store / App Store.
2. `cd expiry-reminder && npm install && npx expo start`
3. Scan the QR code with Expo Go.

Change the reminder time via `REMINDER_HOUR` in `src/notifications.js`.

Note: Expo Go on Android SDK 53+ limits notifications; this project uses SDK 52. For a standalone APK use `npx eas build -p android --profile preview`.
