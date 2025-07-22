'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { GlowingEffect } from './glowing-effect'; 
interface FormWrapperWithEffectProps {
  children: React.ReactNode;
  className?: string;
  // Controls if the glow is active. Set to false if you don't want the dynamic effect
  // but still want the general styling of this wrapper.
  glow?: boolean;
}

export const FormWrapperWithEffect = ({
  children,
  className,
  glow = true, 
}: FormWrapperWithEffectProps) => {
  return (
    <div
      className={cn(
        "relative w-full max-w-md mx-auto rounded-none bg-white p-4 md:rounded-2xl md:p-8 dark:bg-black overflow-hidden", // Added overflow-hidden to contain the glow properly
        className,
      )}
    >
      {/* The form content (titles, paragraphs, actual form fields) goes here */}
      {children}

      {/* The GlowingEffect component creates the dynamic border/shadow */}
      {/* Its `className` is set to match the parent's border-radius for seamless look */}
      <GlowingEffect glow={glow} className="rounded-none md:rounded-2xl" />
    </div>
  );
};