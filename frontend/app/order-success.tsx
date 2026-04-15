import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';

export default function OrderSuccessScreen() {
  const { orderId } = useLocalSearchParams();
  const router = useRouter();
  const scaleAnim = new Animated.Value(0);

  useEffect(() => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      friction: 5,
      tension: 40,
      useNativeDriver: true,
    }).start();
  }, []);

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <View style={styles.content}>
        <Animated.View
          style={[
            styles.iconContainer,
            { transform: [{ scale: scaleAnim }] },
          ]}
        >
          <Ionicons name="checkmark-circle" size={120} color="#10b981" />
        </Animated.View>

        <Text style={styles.title}>Order Placed Successfully!</Text>
        <Text style={styles.subtitle}>
          Thank you for your order. Your medicines will be delivered soon.
        </Text>

        {orderId && (
          <View style={styles.orderIdContainer}>
            <Text style={styles.orderIdLabel}>Order ID</Text>
            <Text style={styles.orderId}>#{orderId.toString().slice(0, 8)}</Text>
          </View>
        )}

        <View style={styles.infoBox}>
          <View style={styles.infoRow}>
            <Ionicons name="time" size={24} color="#10b981" />
            <View style={styles.infoText}>
              <Text style={styles.infoTitle}>Estimated Delivery</Text>
              <Text style={styles.infoSubtitle}>Within 2-3 hours</Text>
            </View>
          </View>
          
          <View style={styles.infoRow}>
            <Ionicons name="notifications" size={24} color="#10b981" />
            <View style={styles.infoText}>
              <Text style={styles.infoTitle}>Order Updates</Text>
              <Text style={styles.infoSubtitle}>You'll receive notifications</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => router.push('/(tabs)/orders')}
        >
          <Text style={styles.primaryButtonText}>View Order</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => router.push('/(tabs)/home')}
        >
          <Text style={styles.secondaryButtonText}>Continue Shopping</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  iconContainer: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  orderIdContainer: {
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 32,
  },
  orderIdLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  orderId: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  infoBox: {
    width: '100%',
    backgroundColor: '#f0fdf4',
    borderRadius: 12,
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  infoText: {
    marginLeft: 16,
    flex: 1,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  infoSubtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  footer: {
    padding: 16,
  },
  primaryButton: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#1f2937',
    fontSize: 18,
    fontWeight: '600',
  },
});
