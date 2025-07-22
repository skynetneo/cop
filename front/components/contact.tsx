"use client";
import React from "react";
import { motion } from "framer-motion";
import MagicButton from "./ui/magic-button";
import { Mail } from "lucide-react";

const ContactSection = () => {
  return (
    <section id="contact" className="w-full py-20 bg-gray-950 text-white text-center">
      <div className="max-w-3xl mx-auto px-4 md:px-8">
        <motion.h2
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-extrabold mb-8"
        >
          Ready to Get Started?
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-neutral-300 leading-relaxed mb-12"
        >
          Join Accessible Solutions today and unlock your full potential.
          Experience peer-based, trauma-informed, and results-driven support tailored just for you.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-8 flex justify-center"
        >
          <MagicButton
            title="Contact Us"
            icon={<Mail className="h-6 w-6" />}
            position="left"
            handleClick={() => window.location.href = "mailto:info@accessiblesolutions.com"}
            otherClasses="min-w-[200px] text-lg md:text-xl py-3 px-8 shadow-lg"
          />
        </motion.div>
      </div>
    </section>
  );
};

export default ContactSection;