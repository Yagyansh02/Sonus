'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

import { ROUTES } from '@/constants';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { Container } from '@/components/layout/container';
import { WavyBackground } from '@/components/ui/wavy-background';

export function HeroSection() {
  return (
    <section className="relative h-screen w-full overflow-hidden bg-black">
      <WavyBackground
        containerClassName="h-full w-full flex flex-col"
        className="w-full flex-1 flex items-center"
        speed="slow"
        waveOpacity={0.35}
        blur={1}
        backgroundFill="#000000"
      >
        {/* ================= Hero Image ================= */}

        <motion.div
          initial={{
            opacity: 0,
            x: 60,
            scale: 0.96,
          }}
          animate={{
            opacity: 1,
            x: 0,
            scale: 1,
          }}
          transition={{
            duration: 0.5,
            ease: 'easeOut',
          }}
          className="
            pointer-events-none
            hidden lg:block
            absolute
            bottom-0
            right-0
            xl:right-[-2%]
            z-10
            h-[124vh]
            aspect-[3/4]
            max-w-[46vw]
          "
        >
          <Image
            src="/hero_girl.png"
            alt="Sonus Music Experience"
            fill
            priority
            sizes="(max-width:1024px) 0px, 45vw"
            className="select-none object-contain object-right-bottom"
          />
        </motion.div>

        {/* ================= Content ================= */}

        <Container className="relative z-20 flex h-full items-center">
          <div className="w-full max-w-[640px] pt-6 lg:pt-0">
            <motion.h1
              initial={{ opacity: 0, y: 35 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
              className="font-heading leading-[1.05] tracking-tight text-primary-text"
            >
              Understand the
              <br />
              <span className="text-gradient">Music</span> That
              <br />
              Moves the World
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7,
                delay: 0.2,
              }}
              className="mt-8 max-w-xl text-lg md:text-xl leading-relaxed text-secondary-text"
            >
              Transcribe, translate, and interpret songs from any language. Powered by AI for deep
              cultural understanding, from slang and metaphors to emotional context and artist
              intent.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7,
                delay: 0.35,
              }}
              className="mt-10"
            >
              <Link href={ROUTES.EXPLORE}>
                <PrimaryButton size="lg" icon={<ArrowRight className="h-4 w-4" />}>
                  Start Exploring
                </PrimaryButton>
              </Link>
            </motion.div>
          </div>
        </Container>
      </WavyBackground>
    </section>
  );
}
