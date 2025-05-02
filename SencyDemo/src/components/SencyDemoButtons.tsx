// SencyDemoButtons.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, Button, ScrollView, DeviceEventEmitter } from 'react-native';
import { startAssessment } from '@sency/react-native-smkit-ui';
import { AssessmentTypes } from '@sency/react-native-smkit-ui/src/SMWorkout';

export default function SencyDemoButtons() {
  const [busy, setBusy] = useState(false);
  const [log, setLog]   = useState<string[]>([]);
  const add = (m:string) =>
    setLog(p => [...p.slice(-40), `${new Date().toLocaleTimeString()} | ${m}`]);

  useEffect(() => {
    const a = DeviceEventEmitter.addListener('workoutDidFinish', () => add('workoutDidFinish'));
    const b = DeviceEventEmitter.addListener('workoutError',      e => add(`workoutError: ${e}`));
    const c = DeviceEventEmitter.addListener('didExitWorkout',    () => add('didExitWorkout'));
    return () => { a.remove(); b.remove(); c.remove(); };
  }, []);

  const run = async () => {
    setBusy(true);
    add('▶️  Starting Fitness assessment');
    try {
      const { summary, didFinish } = await startAssessment(
        AssessmentTypes.Fitness, true, null, false, ''
      );
      add(`✅ Finished (didFinish=${didFinish})`);
      add(summary.slice(0,100)+'…');
    } catch (e:any) {
      add(`❌ ${e}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={{ flex:1, padding:16 }}>
      <Button title="Run Fitness Assessment" onPress={run} disabled={busy}/>
      <ScrollView style={{ marginTop:16, maxHeight:180 }}>
        {log.map((l,i)=> <Text key={i} style={{ fontSize:12, fontFamily:'monospace' }}>{l}</Text>)}
      </ScrollView>
    </View>
  );
}
