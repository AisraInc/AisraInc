// src/components/BodyPartSelector.tsx
import React from 'react';
import { View, Text } from 'react-native';
import RNPickerSelect from 'react-native-picker-select';

export function BodyPartSelector({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { label: string; value: string }[];
}) {
  return (
    <View style={{ margin: 16 }}>
      <Text>Select body part:</Text>
      <RNPickerSelect
        value={value}
        onValueChange={onChange}
        items={options}
        placeholder={{ label: 'Choose…', value: '' }}
      />
    </View>
  );
}
