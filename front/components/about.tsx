"use client";
import React from "react";
import { motion } from "framer-motion";
import { HeartHandshake } from "lucide-react"; 

const AboutSection = () => {
  return (
    <section id="about" className="w-full py-20 bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 md:px-8 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-extrabold mb-10"
        >
          Our Mission
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-neutral-300 leading-relaxed mb-8"
        >
          We believe everyone deserves the opportunity to thrive.
          Our platform is built on the principles of peer-based support, trauma-informed care,
          and a relentless focus on results. We leverage cutting-edge AI to break down barriers
          and provide personalized, effective assistance for career advancement and resource access.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex justify-center items-center gap-4 text-blue-400"
        >
          <HeartHandshake className="h-12 w-12" />
          <p className="text-2xl font-semibold">Empowering Your Journey.</p>
        </motion.div>
      </div>
    </section>
  );
};

export default AboutSection;