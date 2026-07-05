'use client';

import Link from 'next/link';
import { FileText, Languages, MessageCircle } from 'lucide-react';
import { ROUTES } from '@/constants';
import { SecondaryButton } from '@/components/buttons/secondary-button';

interface QuickActionsProps {
  songId: string;
}

/**
 * Action buttons to navigate to different song detail tabs.
 */
export function QuickActions({ songId }: QuickActionsProps) {
  const actions = [
    {
      icon: <FileText className="h-4 w-4" />,
      label: 'View Transcript',
      href: `${ROUTES.SONG(songId)}?tab=transcript`,
    },
    {
      icon: <Languages className="h-4 w-4" />,
      label: 'Translate Lyrics',
      href: `${ROUTES.SONG(songId)}?tab=translation`,
    },
    {
      icon: <MessageCircle className="h-4 w-4" />,
      label: 'Ask AI About This Song',
      href: `${ROUTES.SONG(songId)}?tab=interpretation`,
    },
  ] as const;

  return (
    <div className="flex flex-col justify-center gap-4">
      <h3 className="text-lg font-semibold text-[#F7F2E8] font-heading">
        What would you like to do?
      </h3>
      <div className="flex flex-col gap-3">
        {actions.map((action) => (
          <Link key={action.label} href={action.href}>
            <SecondaryButton
              icon={action.icon}
              className="w-full justify-start"
            >
              {action.label}
            </SecondaryButton>
          </Link>
        ))}
      </div>
    </div>
  );
}
