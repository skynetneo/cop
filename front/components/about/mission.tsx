"use client"

import { motion } from "framer-motion"
import { Shield, Lightbulb, HandHeart, Zap } from "lucide-react"

export default function Mission() {
  const missions = [
    {
      icon: Shield,
      title: "Break Down Barriers",
      description:
        "We eliminate systemic obstacles that prevent people from accessing the help they need, creating pathways to success for everyone.",
    },
    {
      icon: Lightbulb,
      title: "Innovate with Purpose",
      description:
        "Our AI-powered tools are designed with human dignity at the center, enhancing rather than replacing human connection.",
    },
    {
      icon: HandHeart,
      title: "Meet You Where You Are",
      description:
        "No judgment, no prerequisites. We start from your current situation and build a personalized path forward.",
    },
    {
      icon: Zap,
      title: "Deliver Real Results",
      description:
        "Every tool, every interaction, every feature is designed to create measurable positive change in your life.",
    },
  ]

  return (
    <section id="mission" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl lg:text-4xl font-bold text-foreground mb-4"
          >
            Our Mission
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-muted-foreground max-w-3xl mx-auto"
          >
            We're on a mission to make help accessible, effective, and dignified for everyone who needs it.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {missions.map((mission, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="bg-card/30 backdrop-blur-sm rounded-2xl p-8 border border-border hover:border-emerald-500/50 transition-all duration-300"
            >
              <div className="flex items-start space-x-4">
                <div className="bg-emerald-100 dark:bg-emerald-900/30 p-3 rounded-xl">
                  <mission.icon className="w-8 h-8 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-3">{mission.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{mission.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
