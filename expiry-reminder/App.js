import React, { useEffect, useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, Alert, Platform, SafeAreaView, KeyboardAvoidingView,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import DateTimePicker from '@react-native-community/datetimepicker';
import { setupNotifications, scheduleExpiryReminder, cancelReminder, REMINDER_HOUR } from './src/notifications';
import { loadProducts, saveProducts } from './src/storage';

const fmt = (d) => d.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' });
const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
const daysLeft = (iso) => Math.round((startOfDay(new Date(iso)) - startOfDay(new Date())) / 86400000);

export default function App() {
  const [products, setProducts] = useState([]);
  const [name, setName] = useState('');
  const [date, setDate] = useState(new Date());
  const [showPicker, setShowPicker] = useState(false);

  useEffect(() => {
    setupNotifications().then((ok) => {
      if (!ok) Alert.alert('Notifications off', 'Enable notifications in phone settings to get reminders.');
    });
    loadProducts().then(setProducts);
  }, []);

  const persist = (list) => {
    setProducts(list);
    return saveProducts(list);
  };

  const add = async () => {
    const trimmed = name.trim();
    if (!trimmed) return Alert.alert('Enter a product name');
    const notificationId = await scheduleExpiryReminder(trimmed, date);
    if (!notificationId) {
      Alert.alert('Heads up', `The reminder time (${REMINDER_HOUR}:00 on the expiry date) has already passed, so no reminder was set.`);
    }
    const item = { id: String(Date.now()), name: trimmed, expiry: date.toISOString(), notificationId };
    await persist([...products, item].sort((a, b) => new Date(a.expiry) - new Date(b.expiry)));
    setName('');
  };

  const remove = async (item) => {
    await cancelReminder(item.notificationId);
    await persist(products.filter((p) => p.id !== item.id));
  };

  const renderItem = ({ item }) => {
    const left = daysLeft(item.expiry);
    const color = left < 0 ? '#b00020' : left === 0 ? '#e65100' : left <= 3 ? '#f9a825' : '#2e7d32';
    const label = left < 0 ? `Expired ${-left}d ago` : left === 0 ? 'Expires today' : `${left} day${left === 1 ? '' : 's'} left`;
    return (
      <View style={[styles.card, { borderLeftColor: color }]}>
        <View style={{ flex: 1 }}>
          <Text style={styles.cardName}>{item.name}</Text>
          <Text style={styles.cardDate}>{fmt(new Date(item.expiry))}</Text>
          <Text style={[styles.cardLeft, { color }]}>{label}</Text>
        </View>
        <TouchableOpacity onPress={() => remove(item)} style={styles.delBtn}>
          <Text style={styles.delText}>Remove</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <Text style={styles.title}>Expiry Reminder</Text>
        <View style={styles.form}>
          <TextInput style={styles.input} placeholder="Product name" value={name} onChangeText={setName} />
          <TouchableOpacity style={styles.input} onPress={() => setShowPicker(true)}>
            <Text>Expiry date: {fmt(date)}</Text>
          </TouchableOpacity>
          {showPicker && (
            <DateTimePicker
              value={date}
              mode="date"
              minimumDate={new Date()}
              onChange={(_, d) => {
                setShowPicker(Platform.OS === 'ios');
                if (d) setDate(d);
              }}
            />
          )}
          <TouchableOpacity style={styles.addBtn} onPress={add}>
            <Text style={styles.addText}>Add product</Text>
          </TouchableOpacity>
          <Text style={styles.hint}>You'll be reminded at {REMINDER_HOUR}:00 on the expiry date.</Text>
        </View>
        <FlatList
          data={products}
          keyExtractor={(i) => i.id}
          renderItem={renderItem}
          contentContainerStyle={{ padding: 16 }}
          ListEmptyComponent={<Text style={styles.empty}>No products yet.</Text>}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#f5f5f5', paddingTop: Platform.OS === 'android' ? 32 : 0 },
  title: { fontSize: 24, fontWeight: '700', textAlign: 'center', marginVertical: 12 },
  form: { paddingHorizontal: 16 },
  input: { backgroundColor: '#fff', borderRadius: 8, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: '#ddd' },
  addBtn: { backgroundColor: '#1565c0', borderRadius: 8, padding: 14, alignItems: 'center' },
  addText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  hint: { color: '#666', fontSize: 12, textAlign: 'center', marginTop: 6 },
  card: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 8, padding: 12, marginBottom: 10, borderLeftWidth: 6 },
  cardName: { fontSize: 16, fontWeight: '600' },
  cardDate: { color: '#555', marginTop: 2 },
  cardLeft: { marginTop: 2, fontWeight: '600' },
  delBtn: { padding: 8 },
  delText: { color: '#b00020', fontWeight: '600' },
  empty: { textAlign: 'center', color: '#888', marginTop: 30 },
});
