import { Container } from '@/components/layout/container';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading skeleton for the song detail page.
 */
export default function SongDetailLoading() {
  return (
    <div className="pt-24 pb-20">
      <Container>
        {/* Header skeleton */}
        <div className="flex flex-col gap-8 md:flex-row md:items-end md:gap-10 mb-12">
          <Skeleton className="h-56 w-56 shrink-0 md:h-64 md:w-64" />
          <div className="flex flex-col gap-4 flex-1">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-6 w-48" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-24 rounded-full" />
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
          </div>
        </div>

        {/* Tabs skeleton */}
        <div className="flex justify-center mb-8">
          <Skeleton className="h-12 w-96 rounded-full" />
        </div>

        {/* Content skeleton */}
        <Skeleton className="h-96 w-full" />
      </Container>
    </div>
  );
}
