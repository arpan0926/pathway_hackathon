import axios from 'axios';
import type { ChatMessage, ChatRequest } from '../types';

const RAG_URL = import.meta.env.VITE_RAG_API_URL || 'http://localhost:8001';

const ragClient = axios.create({ 
  baseURL: RAG_URL,
  timeout: 30000, // 30s for LLM response
});

export const ragApi = {
  chat: (request: ChatRequest) =>
    ragClient.post<{ answer: string; sources: string[] }>('/chat', request),
};