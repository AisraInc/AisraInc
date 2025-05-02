import axios from 'axios';

const BASE_URL = 'http://192.168.1.5:8000';  // ← your PC’s IPv4 address from ipconfig
// on iOS simulator you can use http://localhost:8000

export interface ChatResponse {
  session_id: string;
  content: {
    type: 'subjective' | 'objective' | 'diagnosis';
    question?: string;
    options?: string[];
    injuries?: string[];
    confidence?: number[];
    [k: string]: any;
  };
  done: boolean;
}

export async function nextChat(
  session_id: string,
  user_input: string
): Promise<ChatResponse> {
  const { data } = await axios.post<ChatResponse>(
    `${BASE_URL}/chat/next`,
    { session_id, user_input }
  );
  return data;
}
