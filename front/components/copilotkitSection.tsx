"use client";
import React from "react";
import { motion } from "framer-motion";
import { Waypoints, FilePenLine, Bot, MapPin } from "lucide-react"; 

import { BentoGrid, BentoGridItem } from "./ui/bento-grid";
import { cn } from "@/lib/utils"; // Assuming this utility is available

const copilotKitFeatures = [
  
  {
    title: "Career Catalyst AI Suite",
    description:
      "Find your ikigai faster with AI-powered Job Search, individually crafted resumes, tailored cover letters, and simulated interview coaching—all personalized in minutes.",
    icon: <Bot className="h-6 w-6 text-purple-400" />,
    className: "md:col-span-1",
    header: (
      <div className="flex h-full w-full flex-1 rounded-xl bg-gradient-to-br from-purple-900 to-indigo-900" />
    ),
  },
  {
    title: "Live Data Sync Engine",
    description:
      "Tap into real-time APIs and databases to fetch the latest service listings, eligibility rules, and deadlines—automatically updated as you work.",
    icon: <Waypoints className="h-6 w-6 text-emerald-400" />,
    className: "md:col-span-1",
    header: (
      <div className="flex h-full w-full flex-1 rounded-xl bg-gradient-to-br from-emerald-900 to-teal-900" />
    ),
  },
  {
    title: "Smart Support Navigator",
    description:
      "Interactive map meets AI assistant: discover local agencies, view hours, and get step-by-step directions or a texted reminders and links so you always know where to go and when.",
    icon: <MapPin className="h-6 w-6 text-red-400" />,
    className: "md:col-span-1",
    header: (
      <div className="flex h-full w-full flex-1 rounded-xl bg-gradient-to-br from-red-900 to-orange-900" />
    ),
  },
  {
    title: "Form Filling Assistant",
    description:
      "Tired of entering the exact same information over and over?? Chat once—submit everywhere. Our AI auto-completes complex applications and forms so you never re-enter the same information twice.",
    icon: <FilePenLine className="h-6 w-6 text-blue-400" />,
    className: "md:col-span-3",
    header: (
      <div className="flex h-full w-full flex-1 rounded-xl bg-gradient-to-br from-blue-900 to-indigo-900" />
    ),
  },
];


const CopilotKitSection = () => {
  return (
    <section id="how-it-works" className="w-full py-20 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <motion.h2
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-extrabold text-center mb-16"
        >
          How We Make AI Work for You
        </motion.h2>

        <BentoGrid className="max-w-4xl mx-auto">
          {copilotKitFeatures.map((item, i) => (
            <BentoGridItem
              key={i}
              title={item.title}
              description={item.description}
              icon={item.icon}
              className={cn(item.className, "bg-neutral-800 border-neutral-700 shadow-md")}
              header={item.header} // Pass the header for background
            />
          ))}
        </BentoGrid>

      </div>
    </section>
  );
};

export default CopilotKitSection;