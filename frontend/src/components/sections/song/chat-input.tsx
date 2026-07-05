'use client';

import { useState, type FormEvent } from 'react';
import { Send } from 'lucide-react';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { Input } from '@/components/ui/input';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

/**
 * Chat input bar with send button.
 * Clears the input after sending.
 */
export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setMessage('');
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-3 border-t border-[rgba(255,255,255,0.08)] bg-[#181818] p-4 rounded-b-[16px]"
    >
      <div className="flex-1">
        <Input
          id="chat-input"
          placeholder="Ask about the song's meaning, cultural references..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={disabled}
        />
      </div>
      <PrimaryButton
        type="submit"
        isLoading={isLoading}
        disabled={!message.trim() || disabled}
        icon={<Send className="h-4 w-4" />}
        size="md"
      >
        Send
      </PrimaryButton>
    </form>
  );
}
