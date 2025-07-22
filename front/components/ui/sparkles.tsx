"use client"

import type React from "react"
import { useRef, useEffect } from "react"

interface SparklesCoreProps {
  count?: number
  colors?: string[]
  minSize?: number
  maxSize?: number
  speed?: number
  fadeOutSpeed?: number
  className?: string
  style?: React.CSSProperties
  particleColor?: string
  particleDensity?: number
  id?: string
  background?: string
  maxParticles?: number
  stopAfterSeconds?: number
}

function SparklesCoreComponent({
  count = 30,
  colors = ["#ffffff", "#10b981", "#3b82f6", "#8b5cf6"],
  minSize = 3,
  maxSize = 7,
  speed = 1,
  fadeOutSpeed = 3,
  className,
  style,
  particleColor,
  particleDensity = 30,
  id,
  background = "transparent",
  maxParticles = 25,
  stopAfterSeconds = 15,
}: SparklesCoreProps) {
  const sparklesRef = useRef<HTMLDivElement>(null)
  const startTimeRef = useRef<number>(Date.now())
  const sparkleElementsRef = useRef<HTMLElement[]>([])

  useEffect(() => {
    const sparkles = sparklesRef.current
    if (!sparkles) return

    startTimeRef.current = Date.now()
    sparkleElementsRef.current = []

    const createSparkle = () => {
      const sparkle = document.createElement("span")
      sparkle.style.position = "absolute"
      sparkle.style.left = `${Math.random() * 100}%`
      sparkle.style.top = `${Math.random() * 100}%`

      const baseSize = Math.random() * (maxSize - minSize) + minSize
      sparkle.style.width = `${baseSize}px`
      sparkle.style.height = sparkle.style.width

      // Use particleColor if provided, otherwise use colors array
      const color = particleColor || colors[Math.floor(Math.random() * colors.length)]
      sparkle.style.backgroundColor = color

      sparkle.style.borderRadius = "50%"
      sparkle.style.opacity = "0.8"
      sparkle.style.pointerEvents = "none"
      sparkle.style.transition = "all 0.3s ease"

      sparkles.appendChild(sparkle)
      sparkleElementsRef.current.push(sparkle)

      // Remove sparkle after a longer duration to keep them around
      setTimeout(
        () => {
          if (sparkle.parentNode) {
            sparkle.remove()
            sparkleElementsRef.current = sparkleElementsRef.current.filter((s) => s !== sparkle)
          }
        },
        30000 + Math.random() * 20000,
      ) // Keep sparkles for 30-50 seconds
    }

    const glowRandomSparkle = () => {
      const activeSparkles = sparkleElementsRef.current.filter((s) => s.parentNode)
      if (activeSparkles.length === 0) return

      const randomSparkle = activeSparkles[Math.floor(Math.random() * activeSparkles.length)]
      const originalSize = Number.parseFloat(randomSparkle.style.width)
      const glowSize = originalSize * (1.5 + Math.random() * 1.5) // 1.5x to 3x size

      // Glow effect
      randomSparkle.style.transform = `scale(${glowSize / originalSize})`
      randomSparkle.style.opacity = "1"
      randomSparkle.style.boxShadow = `0 0 ${glowSize}px ${randomSparkle.style.backgroundColor}`

      // Return to normal after a short time
      setTimeout(
        () => {
          if (randomSparkle.parentNode) {
            randomSparkle.style.transform = "scale(1)"
            randomSparkle.style.opacity = "0.8"
            randomSparkle.style.boxShadow = "none"
          }
        },
        1000 + Math.random() * 2000,
      ) // Glow for 1-3 seconds
    }

    // Create initial sparkles
    const creationInterval = setInterval(() => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000
      const currentCount = sparkleElementsRef.current.filter((s) => s.parentNode).length

      // Stop creating new sparkles after specified time or max count reached
      if (elapsed > stopAfterSeconds || currentCount >= maxParticles) {
        clearInterval(creationInterval)
        return
      }

      createSparkle()
    }, 800) // Create a sparkle every 800ms

    // Start glow effects after initial creation period
    const glowInterval = setInterval(
      () => {
        const elapsed = (Date.now() - startTimeRef.current) / 1000
        if (elapsed > 5) {
          // Start glowing after 5 seconds
          glowRandomSparkle()
        }
      },
      2000 + Math.random() * 3000,
    ) // Random glow every 2-5 seconds

    return () => {
      clearInterval(creationInterval)
      clearInterval(glowInterval)
    }
  }, [colors, count, maxSize, minSize, speed, fadeOutSpeed, particleColor, maxParticles, stopAfterSeconds])

  return (
    <div
      className={className}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "hidden",
        pointerEvents: "none",
        background,
        ...style,
      }}
      ref={sparklesRef}
    />
  )
}

export const SparklesCore = SparklesCoreComponent
export default SparklesCoreComponent
