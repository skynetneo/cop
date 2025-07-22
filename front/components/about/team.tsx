"use client"

import { motion } from "framer-motion"
import { Linkedin, Mail, Heart } from "lucide-react"

export default function Team() {
  const team = [
    {
      name: "Ky Vespera",
      role: "Executive Director",
      bio: "15+ years in nonprofit leadership, AI engineer and community advocate",
      image: "/placeholder.svg?height=300&width=300",
      linkedin: "#",
      email: "ky@accessiblesolutions.org",
    },
    {
      name: "Marcus Chen",
      role: "Chief Technology Officer",
      bio: "Former Google engineer, passionate about AI for social good",
      image: "/placeholder.svg?height=300&width=300",
      linkedin: "#",
      email: "marcus@accessiblesolutions.org",
    },
    {
      name: "Dr. Elena Rodriguez",
      role: "Director of Trauma-Informed Care",
      bio: "Licensed therapist specializing in trauma recovery and resilience",
      image: "/placeholder.svg?height=300&width=300",
      linkedin: "#",
      email: "elena@accessiblesolutions.org",
    },
    {
      name: "James Wilson",
      role: "Peer Support Coordinator",
      bio: "Career transition specialist with personal experience in workforce re-entry",
      image: "/placeholder.svg?height=300&width=300",
      linkedin: "#",
      email: "james@accessiblesolutions.org",
    },
  ]

  return (
    <section id="team" className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl lg:text-4xl font-bold text-foreground mb-4"
          >
            Meet Our Team
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-muted-foreground max-w-3xl mx-auto"
          >
            A diverse group of professionals united by our commitment to making help accessible for everyone.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {team.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border hover:shadow-lg transition-all duration-300 group"
            >
              <div className="text-center">
                <div className="relative mb-6">
                  <img
                    src={member.image || "/placeholder.svg"}
                    alt={member.name}
                    className="w-24 h-24 rounded-full mx-auto object-cover border-4 border-emerald-100 dark:border-emerald-900/30"
                  />
                  <div className="absolute -bottom-2 -right-2 bg-emerald-500 w-6 h-6 rounded-full flex items-center justify-center">
                    <Heart className="w-3 h-3 text-white" />
                  </div>
                </div>

                <h3 className="text-xl font-semibold text-foreground mb-1">{member.name}</h3>
                <p className="text-emerald-600 font-medium mb-3">{member.role}</p>
                <p className="text-muted-foreground text-sm mb-4 leading-relaxed">{member.bio}</p>

                <div className="flex justify-center space-x-3">
                  <a
                    href={member.linkedin}
                    className="bg-muted/50 hover:bg-emerald-100 dark:hover:bg-emerald-900/30 p-2 rounded-lg transition-colors"
                  >
                    <Linkedin className="w-4 h-4 text-muted-foreground hover:text-emerald-600" />
                  </a>
                  <a
                    href={`mailto:${member.email}`}
                    className="bg-muted/50 hover:bg-emerald-100 dark:hover:bg-emerald-900/30 p-2 rounded-lg transition-colors"
                  >
                    <Mail className="w-4 h-4 text-muted-foreground hover:text-emerald-600" />
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
