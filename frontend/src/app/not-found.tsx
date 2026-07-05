import Link from 'next/link';
import { ROUTES } from '@/constants';
import { Container } from '@/components/layout/container';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { ArrowLeft } from 'lucide-react';

/**
 * Custom 404 page.
 */
export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Container>
        <div className="flex flex-col items-center gap-6 text-center">
          <span className="font-heading text-8xl font-bold text-[#F15C43]/20">
            404
          </span>
          <h1 className="font-heading text-4xl">
            Page Not Found
          </h1>
          <p className="text-[#8D8D8D] max-w-md">
            The page you&apos;re looking for doesn&apos;t exist or has been moved. 
            Let&apos;s get you back to the music.
          </p>
          <Link href={ROUTES.HOME}>
            <PrimaryButton icon={<ArrowLeft className="h-4 w-4" />}>
              Back to Home
            </PrimaryButton>
          </Link>
        </div>
      </Container>
    </div>
  );
}
