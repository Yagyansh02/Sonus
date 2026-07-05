'use client';

import Image from 'next/image';
import { motion } from 'framer-motion';
import { Music } from 'lucide-react';
import { Container } from '@/components/layout/container';
import { SongBadges } from '@/components/shared/song-badges';
import type { SongIngestResponse } from '@/types';

interface SongHeaderProps {
  song: SongIngestResponse;
}

/**
 * Hero-style header for the song detail page.
 * Displays thumbnail, title, artist, and metadata badges.
 */
export function SongHeader({ song }: SongHeaderProps) {
  return (
    <div className="relative pt-24 pb-12 md:pt-32 md:pb-16 overflow-hidden">
      {/* Background blur from thumbnail */}
      {song.thumbnail && (
        <div className="absolute inset-0 z-0">
          <Image
            src={song.thumbnail}
            alt=""
            fill
            className="object-cover opacity-20 blur-[60px] scale-110"
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#0D0D0D]/60 via-[#0D0D0D]/80 to-[#0D0D0D]" />
        </div>
      )}

      <Container className="relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
          className="flex flex-col gap-8 md:flex-row md:items-end md:gap-10"
        >
          {/* Thumbnail */}
          <div className="relative h-56 w-56 shrink-0 overflow-hidden rounded-[16px] shadow-[0_8px_40px_rgba(0,0,0,0.5)] md:h-64 md:w-64">
            {song.thumbnail ? (
              <Image
                src={song.thumbnail}
                alt={`${song.title} cover art`}
                fill
                sizes="256px"
                className="object-cover"
                priority
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-[#222222]">
                <Music className="h-16 w-16 text-[#8D8D8D]" />
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex flex-col gap-4">
            <div>
              <p className="text-sm font-medium tracking-wider text-[#8D8D8D] uppercase">
                Song
              </p>
              <h1 className="mt-2 font-heading text-4xl md:text-5xl lg:text-6xl">
                {song.title}
              </h1>
              <p className="mt-2 text-xl text-[#CFC8BE]">{song.artist}</p>
            </div>

            <SongBadges
              genres={song.genres}
              culturalThemes={song.cultural_themes}
              mood={song.mood}
              era={song.era}
              language={song.language}
            />
          </div>
        </motion.div>
      </Container>
    </div>
  );
}
