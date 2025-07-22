"use client"

import { motion } from "framer-motion"
import { TrendingUp, Users, Clock, Award } from "lucide-react"

export default function Impact() {
  const stats = [
    {
      icon: Users,
      number: "1,000+",
      label: "Lives Changed",
      description: "People who have found new opportunities through our platform",
    },
    {
      icon: TrendingUp,
      number: "95%",
      label: "Success Rate",
      description: "Of users achieve their primary goal within 6 months",
    },
    {
      icon: Clock,
      number: "24/7",
      label: "Always Available",
      description: "AI-powered support whenever you need it most",
    },
    {
      icon: Award,
      number: "92%",
      label: "Satisfaction",
      description: "Client satisfaction rate across all our services",
    },
  ]

  return (
    <section
      id="impact"
      className="py-20 bg-gradient-to-r from-emerald-900 to-teal-900 dark:from-emerald-950 dark:to-teal-950 relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-[url('/placeholder.svg?height=400&width=800')] opacity-10 bg-cover bg-center"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl lg:text-4xl font-bold text-white mb-4"
          >
            Our Impact
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-emerald-100 max-w-3xl mx-auto"
          >
            Real numbers from real people whose lives have been transformed through accessible, dignified support.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="text-center bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20"
            >
              <div className="bg-white/20 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <stat.icon className="w-8 h-8 text-emerald-300" />
              </div>
              <div className="text-4xl font-bold text-white mb-2">{stat.number}</div>
              <div className="text-emerald-200 font-semibold mb-2">{stat.label}</div>
              <div className="text-emerald-100 text-sm">{stat.description}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
