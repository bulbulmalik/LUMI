import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { getProfile, updateProfile } from '../api';
import { getToken } from '../storage';

export default function ProfileScreen() {
  const [profile, setProfile] = useState(null);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [language, setLanguage] = useState('');
  const [voiceSpeed, setVoiceSpeed] = useState('1.0');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      const token = await getToken();
      if (!token) return;
      const result = await getProfile(token);
      if (result.user) {
        setProfile(result.user);
        setName(result.user.name || '');
        setPhone(result.user.phone || '');
        setLanguage(result.user.preferred_language || 'en');
        setVoiceSpeed(String(result.user.voice_speed || 1.0));
        setEmergencyContact(result.user.emergency_contact || '');
      }
    }
    load();
  }, []);

  const handleSave = async () => {
    const token = await getToken();
    if (!token) return;

    setLoading(true);
    const result = await updateProfile(token, {
      name,
      phone,
      preferred_language: language,
      voice_speed: parseFloat(voiceSpeed) || 1.0,
      emergency_contact: emergencyContact,
    });
    setLoading(false);

    if (result.user) {
      Alert.alert('Profile saved');
      setProfile(result.user);
      return;
    }

    Alert.alert('Save failed', result.error || 'Unexpected error');
  };

  if (!profile) {
    return (
      <View style={styles.container}>
        <Text>Loading profile...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
      <TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Name" />
      <TextInput style={styles.input} value={phone} onChangeText={setPhone} placeholder="Phone" keyboardType="phone-pad" />
      <TextInput style={styles.input} value={language} onChangeText={setLanguage} placeholder="Language (en)" />
      <TextInput style={styles.input} value={voiceSpeed} onChangeText={setVoiceSpeed} placeholder="Voice speed" keyboardType="decimal-pad" />
      <TextInput
        style={styles.input}
        value={emergencyContact}
        onChangeText={setEmergencyContact}
        placeholder="Emergency contact"
        keyboardType="phone-pad"
      />
      <Button title={loading ? 'Saving…' : 'Save'} onPress={handleSave} disabled={loading} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 18,
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 12,
  },
});
