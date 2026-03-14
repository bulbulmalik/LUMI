import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { login } from '../api';
import { saveToken } from '../storage';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    const result = await login({ email, password });
    setLoading(false);

    if (result.access_token) {
      await saveToken(result.access_token);
      navigation.reset({ index: 0, routes: [{ name: 'Main' }] });
      return;
    }

    Alert.alert('Login failed', result.error || 'Unexpected error');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>LUMI Login</Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title={loading ? 'Logging in…' : 'Log in'} onPress={handleLogin} disabled={loading} />
      <View style={styles.linkRow}>
        <Text>Don't have an account?</Text>
        <Text style={styles.link} onPress={() => navigation.navigate('Register')}>
          Register
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    marginBottom: 24,
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 12,
  },
  linkRow: {
    marginTop: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  link: {
    marginLeft: 8,
    color: '#1976d2',
  },
});
