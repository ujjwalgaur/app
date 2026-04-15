import React from 'react';
import { Stack } from 'expo-router';
import { AuthProvider } from '../contexts/AuthContext';

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="medicine/[id]" />
        <Stack.Screen name="checkout" />
        <Stack.Screen name="order-success" />
      </Stack>
    </AuthProvider>
  );
}
