import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import axios from 'axios';

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

export default function SearchScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (query.trim().length < 2) {
      setMedicines([]);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/medicines`, {
        params: { search: query },
      });
      setMedicines(response.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMedicine = ({ item }: { item: Medicine }) => (
    <TouchableOpacity
      style={styles.medicineItem}
      onPress={() => router.push(`/medicine/${item.id}`)}
    >
      <View style={styles.medicineImageContainer}>
        {item.image ? (
          <Image source={{ uri: item.image }} style={styles.medicineImage} />
        ) : (
          <View style={styles.medicinePlaceholder}>
            <Ionicons name="medical" size={32} color="#d1d5db" />
          </View>
        )}
      </View>
      
      <View style={styles.medicineDetails}>
        <Text style={styles.medicineName}>{item.name}</Text>
        <Text style={styles.medicineSalt} numberOfLines={1}>
          {item.salt_composition}
        </Text>
        <Text style={styles.medicineCategory}>{item.category}</Text>
        
        <View style={styles.bottomRow}>
          <View style={styles.priceContainer}>
            {item.discount > 0 && (
              <Text style={styles.originalPrice}>₹{item.price}</Text>
            )}
            <Text style={styles.finalPrice}>₹{item.final_price}</Text>
          </View>
          
          {item.requires_prescription && (
            <View style={styles.prescriptionBadge}>
              <Ionicons name="document-text" size={12} color="#ef4444" />
              <Text style={styles.prescriptionText}>Rx Required</Text>
            </View>
          )}
        </View>
      </View>
      
      <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Search Medicines</Text>
      </View>

      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9ca3af" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search by name or composition..."
          placeholderTextColor="#9ca3af"
          value={searchQuery}
          onChangeText={handleSearch}
          autoFocus
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => handleSearch('')}>
            <Ionicons name="close-circle" size={20} color="#9ca3af" />
          </TouchableOpacity>
        )}
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : medicines.length > 0 ? (
        <FlatList
          data={medicines}
          renderItem={renderMedicine}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
        />
      ) : searchQuery.length >= 2 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="search-outline" size={64} color="#d1d5db" />
          <Text style={styles.emptyText}>No medicines found</Text>
          <Text style={styles.emptySubtext}>Try searching with different keywords</Text>
        </View>
      ) : (
        <View style={styles.emptyContainer}>
          <Ionicons name="medical-outline" size={64} color="#d1d5db" />
          <Text style={styles.emptyText}>Start searching</Text>
          <Text style={styles.emptySubtext}>Type at least 2 characters to search</Text>
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
  header: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    height: 48,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#1f2937',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    paddingHorizontal: 16,
  },
  medicineItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  medicineImageContainer: {
    marginRight: 12,
  },
  medicineImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
  },
  medicinePlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  medicineDetails: {
    flex: 1,
  },
  medicineName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  medicineSalt: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 4,
  },
  medicineCategory: {
    fontSize: 12,
    color: '#10b981',
    marginBottom: 8,
  },
  bottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
    backgroundColor: '#fef2f2',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  prescriptionText: {
    fontSize: 10,
    color: '#ef4444',
    marginLeft: 4,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6b7280',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 8,
    textAlign: 'center',
  },
});
