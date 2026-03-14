import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import RecentScreen from '../screens/RecentScreen';
import SettingsScreen from '../screens/SettingsScreen';
import NavigationActiveScreen from '../screens/NavigationActiveScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: '#000', borderTopColor: '#222' },
        tabBarActiveTintColor: '#FFE600',
        tabBarInactiveTintColor: '#888',
        tabBarLabelStyle: { fontWeight: '700' },
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarLabel: 'HOME' }} />
      <Tab.Screen name="Recent" component={RecentScreen} options={{ tabBarLabel: 'HISTORY' }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ tabBarLabel: 'SETTINGS' }} />
    </Tab.Navigator>
  );
}

export default function StackNavigator({ initialRouteName }) {
  return (
    <Stack.Navigator initialRouteName={initialRouteName} screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="Main" component={MainTabs} />
      <Stack.Screen name="NavigationActive" component={NavigationActiveScreen} />
    </Stack.Navigator>
  );
}
