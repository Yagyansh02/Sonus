import { cn } from '@/lib/cn';
import { User, Bot } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatMessageProps {
  message: ChatMessageType;
}

/**
 * Individual chat message bubble.
 * User messages align right; assistant messages align left with accent indicator.
 */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          isUser ? 'bg-[#222222] text-[#CFC8BE]' : 'bg-[#F15C43]/15 text-[#F15C43]',
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Bubble */}
      <div
        className={cn(
          'max-w-[80%] rounded-[16px] px-5 py-3',
          isUser
            ? 'bg-[#222222] text-[#F7F2E8]'
            : 'bg-[#1B1B1B] border border-[rgba(255,255,255,0.08)] text-[#CFC8BE]',
        )}
      >
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 border-t border-[rgba(255,255,255,0.06)] pt-3">
            <p className="text-xs font-medium tracking-wider text-[#8D8D8D] uppercase mb-1">
              Sources
            </p>
            <div className="flex flex-wrap gap-1">
              {message.sources.map((source, idx) => (
                <span
                  key={idx}
                  className="inline-block rounded-full bg-[#222222] px-2 py-0.5 text-xs text-[#8D8D8D]"
                >
                  {source}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
