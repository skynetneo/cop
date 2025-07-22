"use client"

import { motion } from "framer-motion"
import { Brain, Users, BarChart3, Heart } from "lucide-react"
import { Meteors } from "@/components/ui/meteors"

export default function Approach() {
  const approaches = [
    {
      icon: Users,
      title: "Peer-Based Support",
      description:
        "Our team includes people with lived experience who understand the challenges you face. We're not just service providers – we're people who've walked similar paths.",
      stats: "95% of clients report feeling understood",
    },
    {
      icon: Heart,
      title: "Trauma-Informed Care",
      description:
        "Every interaction is designed with trauma awareness. We prioritize safety, trustworthiness, collaboration, and empowerment in everything we do.",
      stats: "Reduces re-traumatization by 80%",
    },
    {
      icon: Brain,
      title: "AI-Enhanced, Human-Centered",
      description:
        "Our AI tools amplify human connection rather than replace it. Technology serves people, not the other way around.",
      stats: "3x faster goal achievement",
    },
    {
      icon: BarChart3,
      title: "Data-Driven Results",
      description:
        "We measure what matters: your success. Every program is continuously improved based on real outcomes and client feedback.",
      stats: "92% client satisfaction rate",
    },
  ]

  return (
    <section id="approach" className="py-20 bg-muted/30 relative overflow-hidden">
      <Meteors number={15} />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl lg:text-4xl font-bold text-foreground mb-4"
          >
            Our Approach
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-muted-foreground max-w-3xl mx-auto"
          >
            After over a decade each in nonprofit leadership, our board was tired of the top-down approach. We believe
            in meeting clients where they are, not where we think they should be.
          </motion.p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {approaches.map((approach, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="bg-card/50 backdrop-blur-sm rounded-2xl p-8 border border-border hover:shadow-lg transition-all duration-300"
            >
              <div className="flex items-start space-x-6">
                <div className="bg-emerald-100 dark:bg-emerald-900/30 p-4 rounded-2xl flex-shrink-0">
                  <approach.icon className="w-10 h-10 text-emerald-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-semibold text-foreground mb-4">{approach.title}</h3>
                  <p className="text-muted-foreground mb-4 leading-relaxed">{approach.description}</p>
                  <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-3">
                    <span className="text-emerald-700 dark:text-emerald-300 font-semibold text-sm">
                      {approach.stats}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
