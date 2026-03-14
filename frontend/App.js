import React, { useEffect, useState } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import StackNavigator from './src/navigation/StackNavigator';
import { getToken } from './src/storage';

export default function App() {
  const [isReady, setIsReady] = useState(false);
  const [initialRoute, setInitialRoute] = useState('Login');

  useEffect(() => {
    async function init() {
      const token = await getToken();
      setInitialRoute(token ? 'Main' : 'Login');
      setIsReady(true);
    }
    init();
  }, []);

  if (!isReady) {
    return null;
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <NavigationContainer>
        <StackNavigator initialRouteName={initialRoute} />
      </NavigationContainer>
    </GestureHandlerRootView>
  );
}
