import { Badge } from '@/components/ui/badge';
import { Music2, Palette, Clock, Globe } from 'lucide-react';

interface SongBadgesProps {
  genres?: string[];
  culturalThemes?: string[];
  mood?: string;
  era?: string;
  language?: string;
}

/**
 * Grouped badge display for song metadata.
 * Renders genres, cultural themes, mood, era, and language as pills.
 */
export function SongBadges({
  genres = [],
  culturalThemes = [],
  mood,
  era,
  language,
}: SongBadgesProps) {
  const hasAny =
    genres.length > 0 ||
    culturalThemes.length > 0 ||
    mood ||
    era ||
    (language && language !== 'Unknown');

  if (!hasAny) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {language && language !== 'Unknown' && (
        <Badge variant="outline">
          <Globe className="mr-1 h-3 w-3" />
          {language}
        </Badge>
      )}
      {mood && (
        <Badge variant="accent">
          <Palette className="mr-1 h-3 w-3" />
          {mood}
        </Badge>
      )}
      {era && (
        <Badge variant="outline">
          <Clock className="mr-1 h-3 w-3" />
          {era}
        </Badge>
      )}
      {genres.map((genre) => (
        <Badge key={genre}>
          <Music2 className="mr-1 h-3 w-3" />
          {genre}
        </Badge>
      ))}
      {culturalThemes.map((theme) => (
        <Badge key={theme} variant="accent">
          {theme}
        </Badge>
      ))}
    </div>
  );
}
