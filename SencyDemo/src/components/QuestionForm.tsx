// QuestionForm.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, Button } from 'react-native';
import RNPickerSelect from 'react-native-picker-select';

export function QuestionForm({
  question,
  type,
  options,
  onSubmit,
}: {
  question: string;
  type: 'subjective' | 'objective';
  options?: string[];
  onSubmit: (answer: string) => void;
}) {
  const [answer, setAnswer] = useState('');
  return (
    <View style={{ padding: 16 }}>
      <Text style={{ fontSize: 16, marginBottom: 8 }}>{question}</Text>
      {type === 'subjective' ? (
        <TextInput
          style={{
            borderWidth: 1,
            padding: 8,
            marginBottom: 12,
            borderRadius: 4,
          }}
          value={answer}
          onChangeText={setAnswer}
          placeholder="Type your answer…"
        />
      ) : (
        <RNPickerSelect
          value={answer}
          onValueChange={setAnswer}
          items={options?.map(o => ({ label: o, value: o })) ?? []}
          placeholder={{ label: 'Choose…', value: '' }}
        />
      )}
      <Button
        title="Submit"
        onPress={() => {
          if (answer) onSubmit(answer);
        }}
        disabled={!answer}
      />
    </View>
  );
}
