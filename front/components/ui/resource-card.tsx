"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, Phone, Clock, ExternalLink } from "lucide-react"
import { motion } from "framer-motion"

export interface Resource {
  id: string
  name: string
  services: string[]
  address: string
  phone: string
  hours: string
  website?: string
  coords: {
    lat: number
    lng: number
  }
}

interface ResourceCardProps {
  resource: Resource
  index: number
}

export function ResourceCard({ resource, index }: ResourceCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
    >
      <Card className="w-80 flex-shrink-0 border border-emerald-200 dark:border-emerald-800 hover:shadow-lg transition-shadow">
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div>
              <h3 className="font-semibold text-foreground text-lg leading-tight">{resource.name}</h3>
              <div className="flex flex-wrap gap-1 mt-2">
                {resource.services.slice(0, 3).map((service, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 px-2 py-1 rounded-full"
                  >
                    {service}
                  </span>
                ))}
                {resource.services.length > 3 && (
                  <span className="text-xs text-muted-foreground">+{resource.services.length - 3} more</span>
                )}
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-2">
              <div className="flex items-start space-x-2 text-sm">
                <MapPin className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-muted-foreground">{resource.address}</span>
              </div>

              <div className="flex items-center space-x-2 text-sm">
                <Phone className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <a href={`tel:${resource.phone}`} className="text-emerald-600 hover:underline">
                  {resource.phone}
                </a>
              </div>

              <div className="flex items-start space-x-2 text-sm">
                <Clock className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-muted-foreground">{resource.hours}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-2 pt-2">
              <Button size="sm" className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white">
                <Phone className="w-3 h-3 mr-1" />
                Call
              </Button>
              {resource.website && (
                <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Visit
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface ResourceCarouselProps {
  resources: Resource[]
}

export function ResourceCarousel({ resources }: ResourceCarouselProps) {
  if (resources.length === 0) return null

  return (
    <div className="my-4">
      <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-emerald-200 dark:scrollbar-thumb-emerald-800">
        {resources.map((resource, index) => (
          <ResourceCard key={resource.id} resource={resource} index={index} />
        ))}
      </div>
      {resources.length > 1 && (
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Scroll to see all {resources.length} resources →
        </p>
      )}
    </div>
  )
}
