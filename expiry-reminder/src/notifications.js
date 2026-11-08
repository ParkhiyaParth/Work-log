import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

// Hour (24h, local time) at which the "remove from shelf" reminder fires on the expiry date.
export const REMINDER_HOUR = 21;

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: true, shouldSetBadge: false }),
});

export async function setupNotifications() {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('expiry', {
      name: 'Expiry reminders',
      importance: Notifications.AndroidImportance.HIGH,
    });
  }
  const { status } = await Notifications.getPermissionsAsync();
  if (status === 'granted') return true;
  const res = await Notifications.requestPermissionsAsync();
  return res.status === 'granted';
}

// Returns the notification id, or null if the reminder time has already passed.
export async function scheduleExpiryReminder(name, expiry) {
  const when = new Date(expiry.getFullYear(), expiry.getMonth(), expiry.getDate(), REMINDER_HOUR, 0, 0);
  if (when.getTime() <= Date.now()) return null;
  return Notifications.scheduleNotificationAsync({
    content: {
      title: 'Expires today!',
      body: `Remove "${name}" from the shelf.`,
      sound: true,
    },
    trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: when, channelId: 'expiry' },
  });
}

export async function cancelReminder(id) {
  if (id) await Notifications.cancelScheduledNotificationAsync(id);
}
