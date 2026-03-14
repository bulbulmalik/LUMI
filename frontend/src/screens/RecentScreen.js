import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const sampleItems = [
  {
    id: '1',
    title: 'CAUTION: WET FLOOR',
    time: '2 minutes ago',
  },
  {
    id: '2',
    title: 'EXIT 24B - DOWNTOWN',
    time: '15 minutes ago',
  },
  {
    id: '3',
    title: 'PLATFORM 9 - EXPRESS',
    time: 'Yesterday, 6:45 PM',
  },
  {
    id: '4',
    title: 'WAY OUT -> NO ENTRY',
    time: 'Yesterday, 2:10 PM',
  },
];

export default function RecentScreen() {
  const navigation = useNavigation();

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card} activeOpacity={0.8}>
      <View style={styles.cardRow}>
        <View style={styles.icon}>
          <Text style={styles.iconText}>🔊</Text>
        </View>
        <View style={styles.cardText}>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardTime}>{item.time}</Text>
        </View>
        <Text style={styles.chevron}>{'>'}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backIcon}>{'←'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>RECENT SIGNS</Text>
        <View style={styles.filterRow}>
          <View style={[styles.filterDot, { backgroundColor: '#FFE600' }]} />
          <View style={[styles.filterDot, { backgroundColor: '#FFFFFF' }]} />
          <View style={[styles.filterDot, { backgroundColor: '#1CC0FF' }]} />
        </View>
      </View>

      <Text style={styles.sectionLabel}>TODAY</Text>

      <FlatList
        data={sampleItems}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingTop: 40,
    paddingHorizontal: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 18,
  },
  backButton: {
    padding: 10,
    borderRadius: 12,
    backgroundColor: '#FFE600',
    marginRight: 12,
  },
  backIcon: {
    fontSize: 18,
    fontWeight: '900',
  },
  headerTitle: {
    flex: 1,
    color: '#FFF',
    fontSize: 22,
    fontWeight: '800',
  },
  filterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: 80,
  },
  filterDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFF',
  },
  sectionLabel: {
    color: '#FFE600',
    fontSize: 16,
    fontWeight: '800',
    marginBottom: 12,
  },
  list: {
    paddingBottom: 120,
  },
  card: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 14,
    marginBottom: 12,
  },
  cardRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    width: 50,
    height: 50,
    backgroundColor: '#FFE600',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  iconText: {
    fontSize: 22,
  },
  cardText: {
    flex: 1,
  },
  cardTitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '900',
  },
  cardTime: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
    marginTop: 4,
  },
  chevron: {
    color: '#FFF',
    fontSize: 24,
    marginLeft: 12,
  },
});
