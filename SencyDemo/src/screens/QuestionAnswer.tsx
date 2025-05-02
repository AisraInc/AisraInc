// QuestionAnswer.tsx
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { QuestionForm } from '../components/QuestionForm';
import { nextChat } from '../utils/api';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type RootStackParamList = {
  Workout: undefined;
  AskInjury: undefined;
  QuestionAnswer: { sessionId: string };
  Analysis: { injuries: string[]; confidence: number[] };
};

type Props = NativeStackScreenProps<RootStackParamList, 'QuestionAnswer'>;

export function QuestionAnswer({ route, navigation }:Props) {
  const { sessionId } = route.params;
  const [history, setHistory] = useState<string[]>([]);
  const [current, setCurrent] = useState<{
    type: 'subjective' | 'objective'  ;
    question: string;
    options?: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Kick off with the initial body-part as "answer"
    runNext(sessionId);
  }, []);

  async function runNext(answer: string) {
    setLoading(true);
    try {
      const resp = await nextChat(sessionId, answer);
      if (resp.done) {
        navigation.replace('Analysis', {
          injuries: resp.content.injuries!,
          confidence: resp.content.confidence!,
        });
      } else {
        const { type, question, options } = resp.content;

        if (type === 'diagnosis') {
            // jump straight to analysis screen
            navigation.replace('Analysis', {
              injuries: resp.content.injuries!,
              confidence: resp.content.confidence!,
            });
            return;  // <-- exit before we ever try to setCurrent
          }
      
          setCurrent({ type, question: question!, options });

        setHistory(h => [...h, answer]);
      }
    } finally {
      setLoading(false);
    }
  }

  if (loading || !current)
    return <ActivityIndicator style={{ flex: 1 }} size="large" />;

  return (
    <QuestionForm
      question={current.question}
      type={current.type}
      options={current.options}
      onSubmit={runNext}
    />
  );
}
