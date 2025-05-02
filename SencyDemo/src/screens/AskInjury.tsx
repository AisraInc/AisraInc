// src/screens/AskInjury.tsx
import React, { useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BodyPartSelector } from '../components/BodyPartSelector';

type RootStackParamList = {
    Workout: undefined;
    AskInjury: undefined;
    QuestionAnswer: { sessionId: string };
    Analysis: { injuries: string[]; confidence: number[] };
  };
  
  type Props = NativeStackScreenProps<RootStackParamList, 'AskInjury'>;

export default function AskInjury({ navigation }: Props) {
    const [part, setPart] = useState('');
    const options = [
      { label: 'Ankle', value: 'ankle' },
      { label: 'Knee', value: 'knee' },
      { label: 'Elbow', value: 'elbow' },
      // …
    ];
  
    return (
      <View style={{ flex: 1 }}>
        <BodyPartSelector value={part} onChange={setPart} options={options} />
        <Button
          title="Start Q&A"
          onPress={() =>
            navigation.navigate('QuestionAnswer', { sessionId: part })
          }
          disabled={!part}
        />
      </View>
    );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
