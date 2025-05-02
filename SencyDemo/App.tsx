// App.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Your existing screen, wrapping BootCheck + DemoButtons
import WorkoutScreen from './src/screens/WorkoutScreen';
import AskInjury from './src/screens/AskInjury';
import { QuestionAnswer } from './src/screens/QuestionAnswer';
import { AnalysisScreen } from './src/screens/AnalysisScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="AskInjury">
        <Stack.Screen 
          name="AskInjury" 
          component={AskInjury}
          options={{ title: 'detect injury' }}
        />
        <Stack.Screen 
          name="Workout" 
          component={WorkoutScreen}
          options={{ title: 'Today’s Workout' }}
        />
        <Stack.Screen name="QuestionAnswer"   component={QuestionAnswer}  options={{ title:'Q & A' }}/>
        <Stack.Screen name="Analysis"         component={AnalysisScreen}  options={{ title:'Analysis' }}/>

      </Stack.Navigator>
    </NavigationContainer>
  );
}
