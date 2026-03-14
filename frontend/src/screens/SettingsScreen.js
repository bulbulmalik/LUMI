import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Switch, Alert } from 'react-native';
import Slider from '@react-native-community/slider';

const themes = [
  { id: 'yellow', label: 'YELLOW', color: '#FFE600' },
  { id: 'white', label: 'WHITE', color: '#FFFFFF' },
  { id: 'blue', label: 'BLUE', color: '#1CC0FF' },
];

export default function SettingsScreen() {
  const [theme, setTheme] = useState('yellow');
  const [voiceSpeed, setVoiceSpeed] = useState(1.2);
  const [voiceVolume, setVoiceVolume] = useState(0.8);
  const [haptic, setHaptic] = useState(true);

  const save = () => {
    Alert.alert('Settings saved', 'Your preferences have been updated.');
  };

  const renderThemeOption = (item) => {
    const active = theme === item.id;
    return (
      <TouchableOpacity
        key={item.id}
        style={[styles.themeButton, active && styles.themeButtonActive]}
        onPress={() => setTheme(item.id)}
        activeOpacity={0.8}
      >
        <View
          style={[
            styles.themeDot,
            { backgroundColor: item.color },
            active && { borderColor: '#FFF', borderWidth: 2 },
          ]}
        />
        <Text style={styles.themeLabel}>{item.label}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings & Help</Text>
      </View>

      <Text style={styles.sectionTitle}>VISUAL SETTINGS</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>High Contrast Theme</Text>
        <View style={styles.themeRow}>{themes.map(renderThemeOption)}</View>
      </View>

      <Text style={styles.sectionTitle}>VOICE SETTINGS</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Voice Speed {voiceSpeed.toFixed(1)}x</Text>
        <Slider
          style={styles.slider}
          minimumValue={0.5}
          maximumValue={2.0}
          value={voiceSpeed}
          minimumTrackTintColor="#FFE600"
          maximumTrackTintColor="#555"
          thumbTintColor="#FFE600"
          onValueChange={setVoiceSpeed}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Voice Volume {Math.round(voiceVolume * 100)}%</Text>
        <Slider
          style={styles.slider}
          minimumValue={0.0}
          maximumValue={1.0}
          value={voiceVolume}
          minimumTrackTintColor="#FFE600"
          maximumTrackTintColor="#555"
          thumbTintColor="#FFE600"
          onValueChange={setVoiceVolume}
        />
      </View>

      <View style={styles.cardRow}> 
        <View style={styles.card}>
          <View style={styles.row}>
            <View>
              <Text style={styles.cardTitle}>Haptic Feedback</Text>
              <Text style={styles.cardSubtitle}>Vibrate on interactions</Text>
            </View>
            <Switch
              value={haptic}
              onValueChange={setHaptic}
              thumbColor={haptic ? '#FFE600' : '#ccc'}
              trackColor={{ false: '#444', true: '#666' }}
            />
          </View>
        </View>
      </View>

      <Text style={styles.sectionTitle}>VOICE COMMANDS</Text>
      <View style={styles.card}>
        <Text style={styles.commandTitle}>"Start navigation"</Text>
        <Text style={styles.commandSubtitle}>Begins the route guidance to your active destination.</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.commandTitle}>"Stop navigation"</Text>
        <Text style={styles.commandSubtitle}>Ends the current route and silences alerts.</Text>
      </View>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.actionButton} activeOpacity={0.8}>
          <Text style={styles.actionLabel}>Get Help</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} activeOpacity={0.8}>
          <Text style={styles.actionLabel}>Manual</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={save} activeOpacity={0.8}>
        <Text style={styles.saveText}>SAVE CHANGES</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 18,
    paddingTop: 40,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 18,
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 22,
    fontWeight: '800',
  },
  sectionTitle: {
    color: '#FFE600',
    fontSize: 14,
    fontWeight: '900',
    marginTop: 18,
    marginBottom: 10,
  },
  card: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 14,
    marginBottom: 12,
  },
  cardTitle: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '800',
    marginBottom: 8,
  },
  cardSubtitle: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
    marginTop: 2,
  },
  themeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  themeButton: {
    alignItems: 'center',
    padding: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.3)',
    flex: 1,
    marginRight: 8,
  },
  themeButtonActive: {
    borderColor: '#FFE600',
  },
  themeDot: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginBottom: 8,
  },
  themeLabel: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: '800',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardRow: {
    marginBottom: 12,
  },
  commandTitle: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '800',
    marginBottom: 4,
  },
  commandSubtitle: {
    color: 'rgba(255,255,255,0.75)',
    fontSize: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#111',
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: 'center',
    marginHorizontal: 6,
  },
  actionLabel: {
    color: '#FFE600',
    fontWeight: '900',
  },
  saveButton: {
    marginTop: 18,
    backgroundColor: '#FFE600',
    borderRadius: 18,
    paddingVertical: 16,
    alignItems: 'center',
  },
  saveText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 16,
  },
});
