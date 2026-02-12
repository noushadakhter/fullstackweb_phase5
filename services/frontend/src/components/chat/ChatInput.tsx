'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/Input'; // Assuming Shadcn UI Input component
import { Button } from '@/components/ui/Button'; // Assuming Shadcn UI Button component

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-2 p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
      <Input
        type="text"
        placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="flex-grow rounded-full px-4 py-2 bg-gray-100 dark:bg-gray-700 border-none focus:ring-2 focus:ring-blue-500"
        disabled={isLoading}
      />
      <Button type="submit" disabled={isLoading} className="rounded-full px-4 py-2">
        {isLoading ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.062 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sending...
          </span>
        ) : (
          'Send'
        )}
      </Button>
    </form>
  );
}
