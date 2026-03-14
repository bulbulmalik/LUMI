import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, TextInput, Platform } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getProfile } from '../api';
import { getToken, removeToken } from '../storage';

export default function HomeScreen() {
  const navigation = useNavigation();
  const [profile, setProfile] = useState(null);
  const [command, setCommand] = useState('');
  const [listening, setListening] = useState(false);

  useEffect(() => {
    startContinuousListening();
  }, []);

  const startContinuousListening = () => {
    if (Platform.OS !== 'web') return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase();
      if (speechResult.includes('hey lumi get started') || speechResult.includes('hey lumi') || speechResult.includes('get started')) {
        sendCommand(speechResult);
      }
    };

    recognition.onerror = (event) => {
      console.log('Speech recognition error:', event.error);
      // Restart listening on error
      setTimeout(startContinuousListening, 1000);
    };

    recognition.onend = () => {
      // Restart listening when it ends
      setTimeout(startContinuousListening, 1000);
    };

    recognition.start();
  };

  const handleLogout = async () => {
    await removeToken();
    navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
  };

  const sendCommand = async (text) => {
    if (!text) return;
    const token = await getToken();
    if (!token) return;
    try {
      if (text.toLowerCase().includes('read')) {
        speak('Reading mode activated. Point camera at text.');
        navigation.navigate('NavigationActive', { initialMode: 'reading' });
      } else {
        // Default to navigation for any other command
        const res = await fetch('https://rheostatic-leroy-nonganglionic.ngrok-free.dev/api/navigation/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ command: text })
        });
        if (res.ok) {
          const result = await res.json();
          speak(result.message || 'Navigation started. Scanning for obstacles.');
          navigation.navigate('NavigationActive', { initialMode: 'navigation' });
        } else {
          speak('Failed to start navigation');
          Alert.alert('Error', 'Failed to start navigation');
        }
      }
    } catch (error) {
      speak('Network error');
      Alert.alert('Error', 'Network error');
    }
  };

  const speak = (text) => {
    if (Platform.OS === 'web' && window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      // Select a feminine, empathetic voice
      const voices = window.speechSynthesis.getVoices();
      const softVoice = voices.find(voice => 
        voice.name.includes('Zira') || 
        voice.name.includes('Hazel') || 
        voice.name.includes('Google') && voice.name.includes('Female') ||
        voice.name.includes('Samantha') ||
        voice.name.includes('Female')
      ) || voices.find(voice => voice.name.includes('Female')) || voices[0];
      if (softVoice) utterance.voice = softVoice;
      utterance.rate = 0.75; // Slower for empathy
      utterance.pitch = 1.2; // Higher pitch for femininity
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    }
  };

  const startVoiceInput = () => {
    if (Platform.OS !== 'web') {
      Alert.alert('Voice input not supported on this platform');
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      Alert.alert('Speech recognition not supported in this browser');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onresult = (event) => {
      const speechResult = event.results[event.results.length - 1][0].transcript.toLowerCase();
      if (speechResult.includes('hey lumi get started') || speechResult.includes('hey lumi') || speechResult.includes('get started')) {
        sendCommand(speechResult);
      }
    };
    recognition.onerror = (event) => {
      setListening(false);
      Alert.alert('Voice input error', event.error);
    };
    recognition.onend = () => {
      setListening(false);
      // Optionally restart
      // setTimeout(startVoiceInput, 1000);
    };

    recognition.start();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Lumi</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Settings')}> 
          <Text style={styles.profileIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={[styles.bigButton, styles.startButton]}
        activeOpacity={0.8}
        onPress={() => navigation.navigate('NavigationActive')}
      >
        <Text style={styles.bigButtonText}>START</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.bigButton, styles.stopButton]} activeOpacity={0.8}>
        <Text style={styles.stopButtonText}>STOP</Text>
      </TouchableOpacity>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          placeholder="Say 'Hey Lumi, help me navigate' or 'read this text'"
          value={command}
          onChangeText={setCommand}
        />
        <TouchableOpacity style={styles.sendButton} onPress={() => sendCommand(command)}>
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.sendButton, listening && styles.listeningButton]} onPress={startVoiceInput}>
          <Text style={styles.sendButtonText}>{listening ? '🎤' : 'Voice'}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.8}
        onPress={() => navigation.navigate('Recent')}
      >
        <Text style={styles.cardTitle}>Recent Signs</Text>
        <Text style={styles.cardSubtitle}>View history log</Text>
      </TouchableOpacity>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Choose Theme</Text>
        <View style={styles.themeRow}>
          <View style={[styles.themeDot, { backgroundColor: '#FFE600' }]} />
          <View style={[styles.themeDot, { backgroundColor: '#FFF' }]} />
          <View style={[styles.themeDot, { backgroundColor: '#1CC0FF' }]} />
        </View>
      </View>

      <TouchableOpacity style={styles.card} activeOpacity={0.8}>
        <Text style={styles.cardTitle}>Help</Text>
      </TouchableOpacity>

      <View style={styles.locationCard}>
        <Text style={styles.locationLabel}>Location:</Text>
        <Text style={styles.locationValue}>5th Avenue, NYC</Text>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout} activeOpacity={0.8}>
        <Text style={styles.logoutText}>Log out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    padding: 18,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 18,
  },
  title: {
    color: '#FFF',
    fontSize: 28,
    fontWeight: '900',
  },
  profileIcon: {
    fontSize: 28,
  },
  bigButton: {
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: 12,
  },
  startButton: {
    backgroundColor: '#FFE600',
  },
  stopButton: {
    backgroundColor: '#D60000',
  },
  bigButtonText: {
    fontSize: 24,
    fontWeight: '900',
    color: '#000',
  },
  stopButtonText: {
    fontSize: 24,
    fontWeight: '900',
    color: '#FFF',
  },
  card: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  cardTitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '900',
  },
  cardSubtitle: {
    color: 'rgba(255,255,255,0.7)',
    marginTop: 6,
  },
  themeRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 12,
  },
  themeDot: {
    width: 40,
    height: 40,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#fff',
  },
  locationCard: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 14,
    marginTop: 14,
  },
  locationLabel: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
  },
  locationValue: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '700',
    marginTop: 4,
  },
  logoutButton: {
    marginTop: 18,
    alignSelf: 'center',
  },
  logoutText: {
    color: '#FFE600',
    fontWeight: '900',
  },
  inputContainer: {
    flexDirection: 'row',
    marginTop: 20,
    width: '80%',
    alignSelf: 'center',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    borderRadius: 5,
    marginRight: 10,
    color: '#fff',
    backgroundColor: '#333',
  },
  sendButton: {
    backgroundColor: '#007bff',
    padding: 10,
    borderRadius: 5,
    justifyContent: 'center',
  },
  sendButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  listeningButton: {
    backgroundColor: '#ff0000',
  },
});
