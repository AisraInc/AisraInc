// AnalysisScreen.tsx
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import React from 'react';
import { View, Text, Button, FlatList } from 'react-native';


type RootStackParamList = {
  Workout: undefined;
  AskInjury: undefined;
  QuestionAnswer: { sessionId: string };
  Analysis: { injuries: string[]; confidence: number[] };
};

type Props = NativeStackScreenProps<RootStackParamList, 'Analysis'>;

export function AnalysisScreen({ route, navigation }: Props) {
  const { injuries, confidence } = route.params as {
    injuries: string[];
    confidence: number[];
  };

  return (
    <View style={{ padding: 16 }}>
      <Text style={{ fontSize: 18, marginBottom: 12 }}>Possible Injuries:</Text>
      <FlatList
        data={injuries}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item, index }) => (
          <Text>
            • {item} ({(confidence[index] * 100).toFixed(0)}%)
          </Text>
        )}
      />
      <Button
        title="View Rehab Plan"
        onPress={() => navigation.navigate('Workout')}
      />
    </View>
  );
}
