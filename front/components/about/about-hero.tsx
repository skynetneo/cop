"use client"

import { motion } from "framer-motion"
import { Heart, Users, Target } from "lucide-react"
import { SparklesCore } from "@/components/ui/sparkles"
// import { PointerHighlight } from "@/pointer-highlight"


export default function AboutHero() {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
      <SparklesCore
        id="about-sparkles"
        background="transparent"
        minSize={0.4}
        maxSize={1.0}
        particleDensity={50}
        className="w-full h-full absolute inset-0"
        particleColor="#ffffff"
        colors={["#ffffff", "#10b981", "#3b82f6", "#8b5cf6"]}
        maxParticles={100}
        stopAfterSeconds={12}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center justify-center mb-6"
          >
            <Heart className="w-8 h-8 text-emerald-600 mr-3" />
            <span className="text-emerald-600 font-semibold text-lg">About Accessible Solutions</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl lg:text-6xl font-bold text-foreground mb-6"
          >
            Everyone Deserves to{" "}
            <span className="text-emerald-600 relative">
              Thrive
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 0.8, delay: 0.8 }}
                className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-400 origin-left"
              />
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground mb-12 max-w-4xl mx-auto leading-relaxed"
          >
            At Accessible Solutions, we believe everyone deserves equitable opportunities to thrive. Our platform is
            built on the principles of peer-based support, trauma-informed care, and a relentless focus on results. We
            leverage cutting-edge AI to break down barriers and provide personalized, effective assistance for career
            advancement and resource access.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
          >
            <div className="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border">
              <Users className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Peer-Based Support</h3>
              <p className="text-muted-foreground">Real people who understand your journey</p>
            </div>

            <div className="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border">
              <Heart className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Trauma-Informed Care</h3>
              <p className="text-muted-foreground">Safe, respectful, and healing-centered approach</p>
            </div>

            <div className="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border">
              <Target className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Results-Focused</h3>
              <p className="text-muted-foreground">Measurable outcomes that change lives</p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
