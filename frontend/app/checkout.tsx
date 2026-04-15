import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useCartStore } from '../store/cartStore';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function CheckoutScreen() {
  const [line1, setLine1] = useState('');
  const [line2, setLine2] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [pincode, setPincode] = useState('');
  const [phone, setPhone] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('COD');
  const [loading, setLoading] = useState(false);
  
  const { token, user } = useAuth();
  const cartStore = useCartStore();
  const router = useRouter();

  useEffect(() => {
    if (user?.phone) {
      setPhone(user.phone);
    }
  }, [user]);

  const deliveryCharges = cartStore.total > 500 ? 0 : 50;
  const totalAmount = cartStore.total + deliveryCharges;

  const handlePlaceOrder = async () => {
    if (!line1 || !city || !state || !pincode || !phone) {
      Alert.alert('Error', 'Please fill all address fields');
      return;
    }

    if (pincode.length !== 6) {
      Alert.alert('Error', 'Please enter a valid 6-digit pincode');
      return;
    }

    setLoading(true);
    try {
      const orderData = {
        delivery_address: {
          line1,
          line2,
          city,
          state,
          pincode,
          phone,
        },
        payment_method: paymentMethod,
      };

      const response = await axios.post(`${API_URL}/api/orders`, orderData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      cartStore.clearCart();
      router.replace(`/order-success?orderId=${response.data.id}`);
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to place order'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#1f2937" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Checkout</Text>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Delivery Address</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Address Line 1 *"
              placeholderTextColor="#9ca3af"
              value={line1}
              onChangeText={setLine1}
            />
            
            <TextInput
              style={styles.input}
              placeholder="Address Line 2 (Optional)"
              placeholderTextColor="#9ca3af"
              value={line2}
              onChangeText={setLine2}
            />
            
            <View style={styles.row}>
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="City *"
                placeholderTextColor="#9ca3af"
                value={city}
                onChangeText={setCity}
              />
              
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="State *"
                placeholderTextColor="#9ca3af"
                value={state}
                onChangeText={setState}
              />
            </View>
            
            <View style={styles.row}>
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="Pincode *"
                placeholderTextColor="#9ca3af"
                keyboardType="number-pad"
                maxLength={6}
                value={pincode}
                onChangeText={setPincode}
              />
              
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="Phone *"
                placeholderTextColor="#9ca3af"
                keyboardType="phone-pad"
                maxLength={10}
                value={phone}
                onChangeText={setPhone}
              />
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Payment Method</Text>
            
            <TouchableOpacity
              style={[
                styles.paymentOption,
                paymentMethod === 'COD' && styles.paymentOptionActive,
              ]}
              onPress={() => setPaymentMethod('COD')}
            >
              <View style={styles.paymentLeft}>
                <Ionicons name="cash" size={24} color="#10b981" />
                <View style={styles.paymentInfo}>
                  <Text style={styles.paymentTitle}>Cash on Delivery</Text>
                  <Text style={styles.paymentSubtitle}>Pay when you receive</Text>
                </View>
              </View>
              <View
                style={[
                  styles.radio,
                  paymentMethod === 'COD' && styles.radioActive,
                ]}
              >
                {paymentMethod === 'COD' && (
                  <View style={styles.radioDot} />
                )}
              </View>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.paymentOption,
                paymentMethod === 'ONLINE' && styles.paymentOptionActive,
              ]}
              onPress={() => setPaymentMethod('ONLINE')}
            >
              <View style={styles.paymentLeft}>
                <Ionicons name="card" size={24} color="#10b981" />
                <View style={styles.paymentInfo}>
                  <Text style={styles.paymentTitle}>Online Payment</Text>
                  <Text style={styles.paymentSubtitle}>UPI, Cards, Wallets</Text>
                </View>
              </View>
              <View
                style={[
                  styles.radio,
                  paymentMethod === 'ONLINE' && styles.radioActive,
                ]}
              >
                {paymentMethod === 'ONLINE' && (
                  <View style={styles.radioDot} />
                )}
              </View>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Order Summary</Text>
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Items ({cartStore.items.length})</Text>
              <Text style={styles.summaryValue}>₹{cartStore.total.toFixed(2)}</Text>
            </View>
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Delivery Charges</Text>
              <Text style={styles.summaryValue}>
                {deliveryCharges === 0 ? 'FREE' : `₹${deliveryCharges.toFixed(2)}`}
              </Text>
            </View>
            
            {cartStore.total > 500 && (
              <Text style={styles.freeDeliveryText}>
                You saved ₹50 on delivery charges!
              </Text>
            )}
            
            <View style={[styles.summaryRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>Total Amount</Text>
              <Text style={styles.totalValue}>₹{totalAmount.toFixed(2)}</Text>
            </View>
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.placeOrderButton, loading && styles.buttonDisabled]}
            onPress={handlePlaceOrder}
            disabled={loading}
          >
            <Text style={styles.placeOrderText}>
              {loading ? 'Placing Order...' : 'Place Order'}
            </Text>
            <Text style={styles.placeOrderAmount}>₹{totalAmount.toFixed(2)}</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  content: {
    flex: 1,
  },
  section: {
    padding: 16,
    borderBottomWidth: 8,
    borderBottomColor: '#f3f4f6',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  input: {
    backgroundColor: '#f9fafb',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1f2937',
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfInput: {
    flex: 1,
  },
  paymentOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  paymentOptionActive: {
    borderColor: '#10b981',
    backgroundColor: '#f0fdf4',
  },
  paymentLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  paymentInfo: {
    marginLeft: 12,
  },
  paymentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  paymentSubtitle: {
    fontSize: 13,
    color: '#6b7280',
    marginTop: 2,
  },
  radio: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#d1d5db',
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioActive: {
    borderColor: '#10b981',
  },
  radioDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#10b981',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 15,
    color: '#6b7280',
  },
  summaryValue: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1f2937',
  },
  freeDeliveryText: {
    fontSize: 13,
    color: '#10b981',
    fontWeight: '600',
    marginBottom: 12,
  },
  totalRow: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    marginTop: 4,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  totalValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#10b981',
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  placeOrderButton: {
    flexDirection: 'row',
    backgroundColor: '#10b981',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  placeOrderText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  placeOrderAmount: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
});
