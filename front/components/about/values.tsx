"use client"

import { motion } from "framer-motion"
import { Compass, Eye, Handshake, Rocket, Shield, Sparkles } from "lucide-react"

export default function Values() {
  const values = [
    {
      icon: Compass,
      title: "Dignity First",
      description: "Every person deserves to be treated with respect, regardless of their circumstances.",
    },
    {
      icon: Eye,
      title: "Radical Transparency",
      description: "We're open about our methods, our data, and our challenges. Trust is earned through honesty.",
    },
    {
      icon: Handshake,
      title: "Collaborative Partnership",
      description:
        "You're the expert on your own life. We're here to provide tools and support, not dictate solutions.",
    },
    {
      icon: Rocket,
      title: "Innovation with Impact",
      description: "We embrace new technologies and approaches, but only if they genuinely improve outcomes.",
    },
    {
      icon: Shield,
      title: "Safety & Privacy",
      description: "Your data, your story, and your journey are protected with the highest standards of security.",
    },
    {
      icon: Sparkles,
      title: "Continuous Learning",
      description: "We're always improving, always listening, and always evolving based on your feedback.",
    },
  ]

  return (
    <section id="values" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl lg:text-4xl font-bold text-foreground mb-4"
          >
            Our Values
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-muted-foreground max-w-3xl mx-auto"
          >
            These principles guide every decision we make and every interaction we have.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {values.map((value, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group bg-card/20 backdrop-blur-sm rounded-2xl p-6 border border-border hover:border-emerald-500/50 hover:bg-card/40 transition-all duration-300"
            >
              <div className="text-center">
                <div className="bg-emerald-100 dark:bg-emerald-900/30 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <value.icon className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">{value.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{value.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
