import { create } from 'zustand';

interface CartItem {
  medicine_id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

interface CartStore {
  items: CartItem[];
  total: number;
  addItem: (item: CartItem) => void;
  updateQuantity: (medicine_id: string, quantity: number) => void;
  removeItem: (medicine_id: string) => void;
  clearCart: () => void;
  setCart: (items: CartItem[], total: number) => void;
  getItemCount: () => number;
}

export const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  total: 0,
  
  addItem: (item) => set((state) => {
    const existingItem = state.items.find((i) => i.medicine_id === item.medicine_id);
    
    if (existingItem) {
      const newItems = state.items.map((i) =>
        i.medicine_id === item.medicine_id
          ? { ...i, quantity: i.quantity + item.quantity }
          : i
      );
      const newTotal = newItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
      return { items: newItems, total: newTotal };
    }
    
    const newItems = [...state.items, item];
    const newTotal = newItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
    return { items: newItems, total: newTotal };
  }),
  
  updateQuantity: (medicine_id, quantity) => set((state) => {
    if (quantity <= 0) {
      const newItems = state.items.filter((i) => i.medicine_id !== medicine_id);
      const newTotal = newItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
      return { items: newItems, total: newTotal };
    }
    
    const newItems = state.items.map((i) =>
      i.medicine_id === medicine_id ? { ...i, quantity } : i
    );
    const newTotal = newItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
    return { items: newItems, total: newTotal };
  }),
  
  removeItem: (medicine_id) => set((state) => {
    const newItems = state.items.filter((i) => i.medicine_id !== medicine_id);
    const newTotal = newItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
    return { items: newItems, total: newTotal };
  }),
  
  clearCart: () => set({ items: [], total: 0 }),
  
  setCart: (items, total) => set({ items, total }),
  
  getItemCount: () => {
    const state = get();
    return state.items.reduce((sum, item) => sum + item.quantity, 0);
  },
}));
