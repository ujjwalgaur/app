import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { useCartStore } from '../../store/cartStore';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Medicine {
  id: string;
  name: string;
  salt_composition: string;
  category: string;
  price: number;
  discount: number;
  final_price: number;
  stock_quantity: number;
  description: string;
  usage: string;
  manufacturer: string;
  requires_prescription: boolean;
  image?: string;
  rating: number;
  substitutes: Array<{ id: string; name: string; price: number }>;
}

export default function MedicineDetailScreen() {
  const { id } = useLocalSearchParams();
  const [medicine, setMedicine] = useState<Medicine | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const { token } = useAuth();
  const cartStore = useCartStore();
  const router = useRouter();

  useEffect(() => {
    loadMedicine();
  }, [id]);

  const loadMedicine = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/medicines/${id}`);
      setMedicine(response.data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load medicine details');
      router.back();
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!medicine) return;

    try {
      await axios.post(
        `${API_URL}/api/cart/add`,
        {
          medicine_id: medicine.id,
          quantity,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      cartStore.addItem({
        medicine_id: medicine.id,
        name: medicine.name,
        price: medicine.final_price,
        quantity,
        image: medicine.image,
      });

      Alert.alert('Success', 'Added to cart', [
        { text: 'Continue Shopping', style: 'cancel' },
        { text: 'View Cart', onPress: () => router.push('/(tabs)/cart') },
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to add to cart');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    );
  }

  if (!medicine) {
    return null;
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#1f2937" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Medicine Details</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.imageContainer}>
          {medicine.image ? (
            <Image source={{ uri: medicine.image }} style={styles.image} />
          ) : (
            <View style={styles.imagePlaceholder}>
              <Ionicons name="medical" size={80} color="#d1d5db" />
            </View>
          )}
          {medicine.discount > 0 && (
            <View style={styles.discountBadge}>
              <Text style={styles.discountText}>{medicine.discount}% OFF</Text>
            </View>
          )}
        </View>

        <View style={styles.detailsContainer}>
          <View style={styles.titleRow}>
            <View style={styles.titleContainer}>
              <Text style={styles.name}>{medicine.name}</Text>
              <Text style={styles.manufacturer}>by {medicine.manufacturer}</Text>
            </View>
            <View style={styles.ratingContainer}>
              <Ionicons name="star" size={20} color="#fbbf24" />
              <Text style={styles.ratingText}>{medicine.rating}</Text>
            </View>
          </View>

          <View style={styles.priceRow}>
            {medicine.discount > 0 && (
              <Text style={styles.originalPrice}>₹{medicine.price}</Text>
            )}
            <Text style={styles.finalPrice}>₹{medicine.final_price}</Text>
            {medicine.discount > 0 && (
              <View style={styles.savingsBadge}>
                <Text style={styles.savingsText}>
                  Save ₹{(medicine.price - medicine.final_price).toFixed(2)}
                </Text>
              </View>
            )}
          </View>

          {medicine.requires_prescription && (
            <View style={styles.prescriptionAlert}>
              <Ionicons name="warning" size={20} color="#ef4444" />
              <Text style={styles.prescriptionText}>
                Prescription Required - Upload prescription at checkout
              </Text>
            </View>
          )}

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Composition</Text>
            <Text style={styles.sectionContent}>{medicine.salt_composition}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Description</Text>
            <Text style={styles.sectionContent}>{medicine.description}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Usage</Text>
            <Text style={styles.sectionContent}>{medicine.usage}</Text>
          </View>

          {medicine.substitutes.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Available Substitutes</Text>
              {medicine.substitutes.map((substitute) => (
                <TouchableOpacity
                  key={substitute.id}
                  style={styles.substituteItem}
                  onPress={() => router.push(`/medicine/${substitute.id}`)}
                >
                  <View style={styles.substituteInfo}>
                    <Text style={styles.substituteName}>{substitute.name}</Text>
                    <Text style={styles.substitutePrice}>₹{substitute.price}</Text>
                  </View>
                  <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
                </TouchableOpacity>
              ))}
            </View>
          )}

          <View style={styles.stockInfo}>
            <Ionicons
              name={medicine.stock_quantity > 0 ? 'checkmark-circle' : 'close-circle'}
              size={20}
              color={medicine.stock_quantity > 0 ? '#10b981' : '#ef4444'}
            />
            <Text
              style={[
                styles.stockText,
                { color: medicine.stock_quantity > 0 ? '#10b981' : '#ef4444' },
              ]}
            >
              {medicine.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
            </Text>
          </View>
        </View>
      </ScrollView>

      {medicine.stock_quantity > 0 && (
        <View style={styles.footer}>
          <View style={styles.quantityContainer}>
            <TouchableOpacity
              style={styles.quantityButton}
              onPress={() => setQuantity(Math.max(1, quantity - 1))}
            >
              <Ionicons name="remove" size={24} color="#10b981" />
            </TouchableOpacity>
            <Text style={styles.quantityText}>{quantity}</Text>
            <TouchableOpacity
              style={styles.quantityButton}
              onPress={() => setQuantity(quantity + 1)}
            >
              <Ionicons name="add" size={24} color="#10b981" />
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.addToCartButton} onPress={handleAddToCart}>
            <Ionicons name="cart" size={24} color="#fff" />
            <Text style={styles.addToCartText}>Add to Cart</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
  imageContainer: {
    position: 'relative',
    backgroundColor: '#f3f4f6',
    paddingVertical: 32,
    alignItems: 'center',
  },
  image: {
    width: 250,
    height: 250,
    borderRadius: 12,
  },
  imagePlaceholder: {
    width: 250,
    height: 250,
    borderRadius: 12,
    backgroundColor: '#e5e7eb',
    justifyContent: 'center',
    alignItems: 'center',
  },
  discountBadge: {
    position: 'absolute',
    top: 16,
    right: 16,
    backgroundColor: '#ef4444',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  discountText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  detailsContainer: {
    padding: 16,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  titleContainer: {
    flex: 1,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  manufacturer: {
    fontSize: 14,
    color: '#6b7280',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef3c7',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    height: 36,
  },
  ratingText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginLeft: 4,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  originalPrice: {
    fontSize: 18,
    color: '#9ca3af',
    textDecorationLine: 'line-through',
    marginRight: 12,
  },
  finalPrice: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#10b981',
    marginRight: 12,
  },
  savingsBadge: {
    backgroundColor: '#d1fae5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  savingsText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#10b981',
  },
  prescriptionAlert: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  prescriptionText: {
    flex: 1,
    fontSize: 13,
    color: '#ef4444',
    marginLeft: 8,
    fontWeight: '600',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 8,
  },
  sectionContent: {
    fontSize: 15,
    color: '#6b7280',
    lineHeight: 22,
  },
  substituteItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  substituteInfo: {
    flex: 1,
  },
  substituteName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  substitutePrice: {
    fontSize: 14,
    color: '#10b981',
    fontWeight: '600',
  },
  stockInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  stockText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    gap: 12,
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    paddingHorizontal: 12,
  },
  quantityButton: {
    padding: 8,
  },
  quantityText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginHorizontal: 16,
    minWidth: 32,
    textAlign: 'center',
  },
  addToCartButton: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#10b981',
    borderRadius: 12,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addToCartText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
});
