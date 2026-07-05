'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { cn } from '@/lib/cn';
import { Badge } from '@/components/ui/badge';
import { Music, Globe, Sparkles } from 'lucide-react';
import type { SongIngestResponse } from '@/types';

interface SongCardProps {
  song: SongIngestResponse;
  onClick?: () => void;
  className?: string;
}

/**
 * Song display card with thumbnail, title, artist, and metadata badges.
 * Used in the Explore page after ingestion and in the Library page.
 */
export function SongCard({ song, onClick, className }: SongCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
      className={cn(
        'group relative overflow-hidden rounded-[16px] border border-[rgba(255,255,255,0.08)]',
        'bg-[#1B1B1B] transition-shadow duration-300',
        'shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        'hover:shadow-[0_12px_40px_rgba(0,0,0,0.4)]',
        onClick && 'cursor-pointer',
        className,
      )}
    >
      {/* Thumbnail */}
      <div className="relative aspect-video w-full overflow-hidden">
        {song.thumbnail ? (
          <Image
            src={song.thumbnail}
            alt={`${song.title} by ${song.artist}`}
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-[#222222]">
            <Music className="h-12 w-12 text-[#8D8D8D]" />
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#1B1B1B] via-transparent to-transparent" />
      </div>

      {/* Content */}
      <div className="flex flex-col gap-3 p-5">
        <div>
          <h3 className="text-lg font-semibold text-[#F7F2E8] line-clamp-1 font-heading">
            {song.title}
          </h3>
          <p className="text-sm text-[#8D8D8D] mt-1">{song.artist}</p>
        </div>

        {/* Metadata badges */}
        <div className="flex flex-wrap gap-1.5">
          {song.language && song.language !== 'Unknown' && (
            <Badge variant="outline">
              <Globe className="mr-1 h-3 w-3" />
              {song.language}
            </Badge>
          )}
          {song.mood && (
            <Badge variant="accent">
              <Sparkles className="mr-1 h-3 w-3" />
              {song.mood}
            </Badge>
          )}
          {song.genres.slice(0, 2).map((genre) => (
            <Badge key={genre}>{genre}</Badge>
          ))}
        </div>
      </div>
    </motion.article>
  );
}
