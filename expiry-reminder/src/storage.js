import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'products';

export async function loadProducts() {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function saveProducts(list) {
  await AsyncStorage.setItem(KEY, JSON.stringify(list));
}
