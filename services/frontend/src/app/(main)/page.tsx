'use client';

import { useEffect } from 'react';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ChatInput } from '@/components/chat/ChatInput';
import { useChat } from '@/hooks/useChat';
import { useAuthStore } from '@/lib/auth';

export default function ChatPage() {
  const { messages, isLoading, sendMessage, messagesEndRef } = useChat();
  const { user, initializeAuth } = useAuthStore();

  useEffect(() => {
    initializeAuth(); // Ensure auth state is loaded on page load
  }, [initializeAuth]);

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-64px)]"> {/* Adjust height based on Navbar */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow messages={messages} isLoading={isLoading} />
      </div>
      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
}
