import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from 'react-native';
import { Camera } from 'expo-camera';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function NavigationActiveScreen({ navigation, route }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [mode, setMode] = useState(route.params?.initialMode || 'navigation'); // 'navigation' or 'reading'
  const cameraRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    startContinuousListening();
  }, []);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      if (status === 'granted') {
        speak('Navigation active. I am scanning for obstacles and will guide you continuously. Say "switch to reading" for text mode or "stop" to exit.');
      }
    })();
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
      if (speechResult.includes('switch to reading') || speechResult.includes('read mode')) {
        setMode('reading');
        speak('Switched to reading mode.');
      } else if (speechResult.includes('switch to navigation') || speechResult.includes('nav mode')) {
        setMode('navigation');
        speak('Switched to navigation mode.');
      } else if (speechResult.includes('stop navigation') || speechResult.includes('stop')) {
        navigation.goBack();
        speak('Navigation stopped.');
      } else if (speechResult.includes('what is') || speechResult.includes('what do you see') || speechResult.includes('what\'s in my hand') || speechResult.includes('tell me what you see')) {
        // Immediate analysis for questions
        analyzeFrame();
      }
    };

    recognition.onerror = (event) => {
      console.log('Speech recognition error:', event.error);
      setTimeout(startContinuousListening, 1000);
    };

    recognition.onend = () => {
      setTimeout(startContinuousListening, 1000);
    };

    recognition.start();
  };

  useEffect(() => {
    if (mode === 'navigation' && hasPermission) {
      // Start automatic analysis every 3 seconds
      intervalRef.current = setInterval(() => {
        analyzeFrame();
      }, 3000);
    } else {
      // Stop automatic analysis
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [mode, hasPermission]);

  const analyzeFrame = async () => {
    if (!cameraRef.current || analyzing) return;
    setAnalyzing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({ base64: true });
      const token = await AsyncStorage.getItem('token');
      const formData = new FormData();
      formData.append('image', {
        uri: photo.uri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });
      formData.append('context', mode);

      const res = await fetch('https://rheostatic-leroy-nonganglionic.ngrok-free.dev/api/vision/analyze', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (res.ok) {
        const result = await res.json();
        const instruction = result.audio_message || 'No obstacles detected';
        speak(instruction);
        Alert.alert('Navigation', instruction);
      } else {
        Alert.alert('Error', 'Failed to analyze image');
      }
    } catch (error) {
      Alert.alert('Error', 'Camera or network error');
    }
    setAnalyzing(false);
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

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Requesting camera permission...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>No access to camera</Text></View>;
  }

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} ref={cameraRef} />
      <View style={styles.overlay}>
        <View style={styles.topRow}>
          <TouchableOpacity style={styles.closeButton} onPress={() => navigation.goBack()}>
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>
          <View style={styles.statusPills}>
            <View style={[styles.statusPill, styles.activePill]}>
              <Text style={styles.statusText}>ACTIVE</Text>
            </View>
            <View style={[styles.dot, { backgroundColor: '#FFE600' }]} />
            <View style={[styles.dot, { backgroundColor: '#FFF' }]} />
            <View style={[styles.dot, { backgroundColor: '#1CC0FF' }]} />
          </View>
        </View>

        <Text style={styles.title}>NAVIGATION</Text>
        <Text style={styles.subtitle}>ACTIVE</Text>

        <View style={styles.circleContainer}>
          <View style={styles.circleOuter}>
            <View style={styles.circleInner}>
              <Text style={styles.eye}>👁️</Text>
              <Text style={styles.scanning}>{analyzing ? 'ANALYZING...' : mode === 'navigation' ? 'AUTO-SCANNING' : 'READY TO SCAN'}</Text>
            </View>
          </View>
        </View>

        <View style={styles.liveRow}>
          <View style={styles.liveDot} />
          <Text style={styles.liveText}>LIVE CAMERA FEED</Text>
        </View>

        {mode === 'reading' && (
          <TouchableOpacity style={styles.analyzeButton} onPress={analyzeFrame} disabled={analyzing}>
            <Text style={styles.analyzeText}>{analyzing ? 'ANALYZING...' : 'ANALYZE NOW'}</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.modeButton} onPress={() => setMode(mode === 'navigation' ? 'reading' : 'navigation')}>
          <Text style={styles.modeText}>Mode: {mode === 'navigation' ? 'Navigation' : 'Reading'}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.stopButton} activeOpacity={0.8}>
          <Text style={styles.stopText}>STOP NAVIGATION</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  camera: {
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  analyzeButton: {
    backgroundColor: '#FFE600',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginTop: 20,
  },
  analyzeText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modeButton: {
    backgroundColor: '#007bff',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginTop: 10,
  },
  modeText: {
    color: 'white',
    fontSize: 14,
  },
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 18,
    paddingTop: 40,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  closeButton: {
    width: 46,
    height: 46,
    borderRadius: 16,
    backgroundColor: '#FFE600',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeText: {
    color: '#000',
    fontSize: 22,
    fontWeight: '900',
  },
  statusPills: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusPill: {
    borderRadius: 20,
    paddingVertical: 6,
    paddingHorizontal: 14,
    backgroundColor: '#111',
  },
  activePill: {
    borderWidth: 2,
    borderColor: '#FFE600',
  },
  statusText: {
    color: '#FFF',
    fontWeight: '900',
    fontSize: 12,
  },
  dot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    borderWidth: 1,
    borderColor: '#FFF',
    marginLeft: 8,
  },
  title: {
    marginTop: 24,
    color: '#FFF',
    fontSize: 22,
    fontWeight: '900',
    textAlign: 'center',
  },
  subtitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 24,
  },
  circleContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  circleOuter: {
    width: 260,
    height: 260,
    borderRadius: 130,
    borderWidth: 10,
    borderColor: '#FFE600',
    justifyContent: 'center',
    alignItems: 'center',
  },
  circleInner: {
    width: 220,
    height: 220,
    borderRadius: 110,
    backgroundColor: '#111',
    justifyContent: 'center',
    alignItems: 'center',
  },
  eye: {
    fontSize: 50,
  },
  scanning: {
    marginTop: 10,
    color: '#FFE600',
    fontSize: 18,
    fontWeight: '900',
  },
  liveRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 14,
  },
  liveDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#FFE600',
    marginRight: 8,
  },
  liveText: {
    color: '#FFF',
    fontWeight: '800',
  },
  alertCard: {
    backgroundColor: '#FFE600',
    borderRadius: 16,
    paddingVertical: 18,
    paddingHorizontal: 14,
    marginTop: 28,
    alignItems: 'center',
  },
  alertText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 18,
  },
  stopButton: {
    marginTop: 16,
    backgroundColor: '#D60000',
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
  },
  stopText: {
    color: '#FFF',
    fontWeight: '900',
    fontSize: 16,
  },
});
