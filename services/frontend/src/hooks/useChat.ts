import { useState, useRef, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import { useAuthStore } from '@/lib/auth';
import { v4 as uuidv4 } from 'uuid'; // For generating UUIDs if needed

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { isLoggedIn, user } = useAuthStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize conversation or load from storage
  useEffect(() => {
    // In a real app, you might load a conversation history from local storage
    // or fetch recent conversations from the API on initial load
    if (isLoggedIn && !conversationId && user) {
      // For now, we'll start with a fresh conversation ID on user login
      // or if no conversation is active.
      // A more robust solution would retrieve active conversation from backend/local storage.
      // Let's just set a welcome message if starting fresh.
      setMessages([
        { role: 'assistant', content: "Hi there! I'm TaskBot, your AI Todo Manager. How can I help you today?" }
      ]);
    } else if (!isLoggedIn) {
      setMessages([]);
      setConversationId(null);
    }
  }, [isLoggedIn, user]);


  const sendMessage = useCallback(async (text: string) => {
    if (!isLoggedIn || !user || !text.trim()) return;

    const userMessage: Message = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const payload = {
        conversation_id: conversationId || undefined,
        message: text,
      };
      
      const response = await api.post<ChatResponse>('/chat', payload);
      const { conversation_id: newConversationId, response: assistantResponse } = response.data;

      if (!conversationId) {
        setConversationId(newConversationId);
      }

      setMessages((prev) => [...prev, { role: 'assistant', content: assistantResponse }]);
    } catch (error: any) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Oops! Something went wrong. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoggedIn, user, conversationId]);

  return {
    messages,
    isLoading,
    sendMessage,
    conversationId,
    messagesEndRef,
  };
}
