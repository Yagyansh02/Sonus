'use client';

import { useRef, useEffect } from 'react';
import { MessageCircle, RotateCcw } from 'lucide-react';
import { useSongStore } from '@/store/song-store';
import { useRag } from '@/hooks/use-rag';
import { ChatMessage } from './chat-message';
import { ChatInput } from './chat-input';
import { EmptyState } from '@/components/shared/empty-state';
import { SecondaryButton } from '@/components/buttons/secondary-button';
import { FadeIn } from '@/components/animations/fade-in';

interface InterpretationTabProps {
  songId: string;
}

/**
 * RAG-powered cultural interpretation chat interface.
 * Displays conversation history and provides a chat input.
 */
export function InterpretationTab({ songId }: InterpretationTabProps) {
  const chatHistory = useSongStore((s) => s.chatHistory);
  const resetChat = useSongStore((s) => s.resetChat);
  const { mutate, isPending } = useRag();
  const scrollRef = useRef<HTMLDivElement>(null);

  /** Auto-scroll to bottom when new messages arrive. */
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory]);

  function handleSend(question: string) {
    mutate({ songId, question });
  }

  return (
    <FadeIn>
      <div
        className="flex flex-col rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#181818] overflow-hidden"
        role="tabpanel"
        id="tabpanel-interpretation"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#F15C43]/15 text-[#F15C43]">
              <MessageCircle className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#F7F2E8]">
                Cultural Interpretation
              </h3>
              <p className="text-xs text-[#8D8D8D]">
                Ask anything about this song
              </p>
            </div>
          </div>
          {chatHistory.length > 0 && (
            <SecondaryButton
              onClick={resetChat}
              size="sm"
              icon={<RotateCcw className="h-3 w-3" />}
            >
              Reset
            </SecondaryButton>
          )}
        </div>

        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex flex-col gap-4 overflow-y-auto p-6"
          style={{ maxHeight: '480px', minHeight: '320px' }}
        >
          {chatHistory.length === 0 ? (
            <EmptyState
              icon={<MessageCircle className="h-10 w-10" />}
              title="Start a Conversation"
              description="Ask about lyrics meaning, cultural references, metaphors, slang, emotional context, or artist intent."
              className="border-none bg-transparent"
            />
          ) : (
            chatHistory.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))
          )}

          {/* Typing indicator */}
          {isPending && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#F15C43]/15 text-[#F15C43]">
                <MessageCircle className="h-4 w-4" />
              </div>
              <div className="rounded-[16px] bg-[#1B1B1B] border border-[rgba(255,255,255,0.08)] px-5 py-3">
                <div className="flex gap-1">
                  <span className="h-2 w-2 rounded-full bg-[#8D8D8D] animate-bounce" />
                  <span className="h-2 w-2 rounded-full bg-[#8D8D8D] animate-bounce [animation-delay:150ms]" />
                  <span className="h-2 w-2 rounded-full bg-[#8D8D8D] animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput onSend={handleSend} isLoading={isPending} />
      </div>
    </FadeIn>
  );
}
