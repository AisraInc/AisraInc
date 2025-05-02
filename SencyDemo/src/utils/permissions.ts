// permissions.ts
import { PermissionsAndroid } from 'react-native';

export async function requestCameraPermission(): Promise<boolean> {
  const result = await PermissionsAndroid.request(
    PermissionsAndroid.PERMISSIONS.CAMERA,
    {
      title: 'Camera Permission',
      message: 'Sency needs access to your camera for exercise detection',
      buttonPositive: 'OK',
      buttonNegative: 'Cancel',
    }
  );
  return result === PermissionsAndroid.RESULTS.GRANTED;
}
