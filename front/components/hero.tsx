"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Heart, Sparkles } from "lucide-react"
import {Vortex} from "@/components/ui/vortex"
import {FlipWords} from "@/components/ui/FlipWords"
import MagicButton from "@/components/ui/magic-button"

export default function Hero() {
  const words = ["accessible", "simple", "effective", "empowering"]

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      <Vortex
        backgroundColor="transparent"
        rangeY={800}
        particleCount={400}
        baseHue={100}
        className="flex items-center flex-col justify-center px-2 md:px-10 py-4 w-full h-full"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="flex items-center mb-8">
                <Heart className="w-6 h-6 text-emerald-600 mr-2" />
                <span className="text-emerald-500 font-bold"><strong>Accessible Solutions</strong> • Oregon</span>
              </div>

              <h1 className="text-4xl lg:text-6xl font-bold text-foreground mb-6">
                Help Happens{" "}
                <span className="text-emerald-400">
                  Here
                </span>
              </h1>

              <p className="text-xl text-muted-foreground mb-8 py-6 leading-relaxed">
                We believe getting help should be simple and accessible. Our peer-based, trauma-informed approach meets
                you where you are and helps you achieve your goals through innovative AI-powered tools and personalized
                support.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <MagicButton
                  title="Start Your Journey"
                  icon={<ArrowRight className="w-5 h-5" />}
                  position="right"
                />
                <Button
                  variant="outline"
                  size="lg"
                  className="border-border hover:bg-accent hover:text-accent-foreground  hover:bg-emerald-700"
                >
                  Learn More
                </Button>
              </div>

              <div className="grid grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">1000+</div>
                  <div className="text-muted-foreground">People Helped</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">24/7</div>
                  <div className="text-muted-foreground">AI Support</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">100%</div>
                  <div className="text-muted-foreground">Free Services</div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-card/50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-border">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse delay-100"></div>
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse delay-200"></div>
                  </div>
                  <div className="space-y-3">
                    <div className="h-4 bg-muted rounded w-3/4"></div>
                    <div className="h-4 bg-emerald-200/30 rounded w-1/2"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                    <div className="h-8 bg-emerald-100/20 rounded-lg flex items-center px-4">
                      <Sparkles className="w-4 h-4 text-emerald-400 mr-2" />
                      <span className="text-emerald-600 font-medium">Sybl AI is ready to help!</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Vortex>
    </section>
  )
}
