// SencyBootCheck.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { configure } from '@sency/react-native-smkit-ui';
import { requestCameraPermission } from '../utils/permissions';

const AUTH_KEY = 'public_live_Pf6Adc441DyxpzxpBI';

export default function SencyBootCheck() {
  const [status, setStatus] = useState<'pending'|'ok'|'fail'>('pending');
  const [err, setErr]       = useState('');

  useEffect(() => {
    (async () => {
      if (!await requestCameraPermission()) {
        setErr('Camera permission denied');
        return setStatus('fail');
      }
      try {
        await configure(AUTH_KEY);
        setStatus('ok');
      } catch (e:any) {
        setErr(e.toString());
        setStatus('fail');
      }
    })();
  }, []);

  const msg =
    status === 'pending' ? '🟡 Initialising…' :
    status === 'ok'      ? '🟢 Sency ready!' :
                           `🔴 ${err}`;

  return (
    <View style={styles.bootBox}>
      <Text style={styles.mono}>{msg}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  mono:   { fontSize: 12, fontFamily: 'monospace' },
  bootBox:{ padding: 12, backgroundColor: '#eee', borderRadius: 8, margin: 16 },
});
