import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  FlatList,
  ActivityIndicator,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

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
  image?: string;
  rating: number;
  requires_prescription: boolean;
}

export default function HomeScreen() {
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadData();
  }, [selectedCategory]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load categories
      const catResponse = await axios.get(`${API_URL}/api/categories`);
      setCategories(['All', ...catResponse.data.categories]);
      
      // Load medicines
      const params = selectedCategory !== 'All' ? { category: selectedCategory } : {};
      const medResponse = await axios.get(`${API_URL}/api/medicines`, { params });
      setMedicines(medResponse.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMedicine = ({ item }: { item: Medicine }) => (
    <TouchableOpacity
      style={styles.medicineCard}
      onPress={() => router.push(`/medicine/${item.id}`)}
    >
      <View style={styles.medicineImageContainer}>
        {item.image ? (
          <Image source={{ uri: item.image }} style={styles.medicineImage} />
        ) : (
          <View style={styles.medicinePlaceholder}>
            <Ionicons name="medical" size={40} color="#d1d5db" />
          </View>
        )}
        {item.discount > 0 && (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>{item.discount}% OFF</Text>
          </View>
        )}
      </View>
      
      <View style={styles.medicineInfo}>
        <Text style={styles.medicineName} numberOfLines={2}>
          {item.name}
        </Text>
        <Text style={styles.medicineSalt} numberOfLines={1}>
          {item.salt_composition}
        </Text>
        
        <View style={styles.ratingContainer}>
          <Ionicons name="star" size={14} color="#fbbf24" />
          <Text style={styles.ratingText}>{item.rating}</Text>
        </View>
        
        <View style={styles.priceContainer}>
          {item.discount > 0 && (
            <Text style={styles.originalPrice}>₹{item.price}</Text>
          )}
          <Text style={styles.finalPrice}>₹{item.final_price}</Text>
        </View>
        
        {item.requires_prescription && (
          <View style={styles.prescriptionBadge}>
            <Ionicons name="document-text" size={12} color="#ef4444" />
            <Text style={styles.prescriptionText}>Rx</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.name || 'User'}!</Text>
          <Text style={styles.subtitle}>What medicines do you need?</Text>
        </View>
        <TouchableOpacity style={styles.notificationButton}>
          <Ionicons name="notifications-outline" size={24} color="#1f2937" />
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.searchBar}
        onPress={() => router.push('/(tabs)/search')}
      >
        <Ionicons name="search" size={20} color="#9ca3af" />
        <Text style={styles.searchPlaceholder}>Search medicines...</Text>
      </TouchableOpacity>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesContainer}
        contentContainerStyle={styles.categoriesContent}
      >
        {categories.map((category) => (
          <TouchableOpacity
            key={category}
            style={[
              styles.categoryChip,
              selectedCategory === category && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(category)}
          >
            <Text
              style={[
                styles.categoryText,
                selectedCategory === category && styles.categoryTextActive,
              ]}
            >
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={medicines}
          renderItem={renderMedicine}
          keyExtractor={(item) => item.id}
          numColumns={2}
          contentContainerStyle={styles.medicinesList}
          columnWrapperStyle={styles.medicinesRow}
          showsVerticalScrollIndicator={false}
        />
      )}
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
    paddingVertical: 16,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginBottom: 16,
  },
  searchPlaceholder: {
    marginLeft: 8,
    fontSize: 16,
    color: '#9ca3af',
  },
  categoriesContainer: {
    maxHeight: 50,
    marginBottom: 16,
  },
  categoriesContent: {
    paddingHorizontal: 16,
  },
  categoryChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: '#10b981',
  },
  categoryText: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '600',
  },
  categoryTextActive: {
    color: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  medicinesList: {
    paddingHorizontal: 8,
    paddingBottom: 16,
  },
  medicinesRow: {
    justifyContent: 'space-between',
  },
  medicineCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    margin: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    maxWidth: '48%',
  },
  medicineImageContainer: {
    position: 'relative',
    alignItems: 'center',
    marginBottom: 8,
  },
  medicineImage: {
    width: '100%',
    height: 120,
    borderRadius: 8,
  },
  medicinePlaceholder: {
    width: '100%',
    height: 120,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  discountBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#ef4444',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  discountText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  medicineInfo: {
    flex: 1,
  },
  medicineName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  medicineSalt: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 8,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  ratingText: {
    fontSize: 12,
    color: '#6b7280',
    marginLeft: 4,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  originalPrice: {
    fontSize: 12,
    color: '#9ca3af',
    textDecorationLine: 'line-through',
    marginRight: 8,
  },
  finalPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#10b981',
  },
  prescriptionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  prescriptionText: {
    fontSize: 10,
    color: '#ef4444',
    marginLeft: 4,
    fontWeight: 'bold',
  },
});
