// src/screens/WorkoutScreen.tsx
import React from 'react';
import { SafeAreaView, StyleSheet, Button } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import SencyBootCheck from '../components/SencyBootCheck';
import SencyDemoButtons from '../components/SencyDemoButtons';

type RootStackParamList = {
  Workout: undefined;
  AskInjury: undefined;
  QuestionAnswer: { sessionId: string };
  Analysis: { injuries: string[]; confidence: number[] };
};

type Props = NativeStackScreenProps<RootStackParamList, 'Workout'>;

export default function WorkoutScreen({ navigation }: Props) {
  return (
    <SafeAreaView style={styles.container}>
      {/* …your existing SencyBootCheck/SencyDemoButtons… */}
    
      <SencyBootCheck />
      <SencyDemoButtons />
    
      <Button
        title="Report an Injury"
        onPress={() => navigation.goBack()}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
});
