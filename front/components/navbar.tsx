"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import {
  Navbar as ResizableNavbar,
  NavBody,
  NavItems,
  NavbarLogo as ImportedNavbarLogo,
  NavbarButton,
  MobileNav,
  MobileNavHeader,
  MobileNavToggle,
  MobileNavMenu,
} from "./ui/resizable-navbar";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
// Removed: import { AnimatedCopilotModal } from "./AnimatedCopilotModal"; // Not needed here anymore
import AccessibleLogo from "@/lib/Accessible.png";
import Image from "next/image";

const navItems = [
  { name: "Resume Builder", link: "/resume-builder" },
  { name: "UpSkilz", link: "/upskilz" },
  { name: "About", link: "/about" },
  { name: "Donate", link: "/donate" },
];


// Logo is now a single, functional component linking to home
const NavbarLogo = () => (
    <a href="/" className="relative z-20 flex items-center gap-2 mr-4">
      <Image src={AccessibleLogo} alt="Accessible Solutions Logo"  width={40} height={40} className="rounded-full " />
      <span className="font-semibold text-white dark:text-white">Accessible Solutions</span>
    </a>
);


export const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  // Removed: const { open: openChat } = useCopilotUI(); (Not directly used here anymore)

  const isActive = (link: string) =>
    link === "/" ? pathname === "/" : pathname.startsWith(link);

  // Removed: handleHelpClick function as it's no longer relevant for the navbar
  // The actual click handler for the "Help" link will be handled by the <a> tag's href.

  return (
    <ResizableNavbar className="top-0">
      <NavBody className="max-w-screen-xl">
        <NavbarLogo />

        {/* Flex container for navigation items */}
        <div className="flex-grow flex justify-center">
          <div className="flex items-center space-x-2 text-sm font-small text-zinc-100">
            {navItems.map((item, idx) => (
              <a
                href={item.link}
                className={cn(
                  "relative px-4 py-2 text-neutral-100 dark:text-neutral-300 transition-colors duration-200 hover:text-purple dark:hover:text-white",
                  { "font-bold text-blue-500 dark:text-blue-400": isActive(item.link) }
                )}
                key={`link-${idx}`}
              >
                {item.name}
              </a>
            ))}
            
          </div>
        </div>

        <NavbarButton href="/auth" className="relative z-20">
          Sign Up / Login
        </NavbarButton>
      </NavBody>

      {/* Mobile Nav */}
      <MobileNav>
        <MobileNavHeader>
          <NavbarLogo />
          <MobileNavToggle
            isOpen={mobileMenuOpen}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          />
        </MobileNavHeader>
        <MobileNavMenu
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        >
          {navItems.map((item, idx) => (
            <a
              key={`mobile-link-${idx}`}
              href={item.link}
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "px-4 py-2 text-lg font-medium text-black dark:text-white",
                { "text-blue-500 dark:text-blue-400 font-bold": isActive(item.link) }
              )}
            >
              {item.name}
            </a>
          ))}
          <NavbarButton href="/auth" className="w-full text-md mt-4" onClick={() => setMobileMenuOpen(false)}>
            Sign Up / Login
          </NavbarButton>
        </MobileNavMenu>
      </MobileNav>
    </ResizableNavbar>
  );
};

export default Navbar;