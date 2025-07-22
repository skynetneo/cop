import { Card, CardContent } from "@/components/ui/card"
import {Meteors} from "@/components/ui/meteors"
import { Brain, GraduationCap, Target, MessageCircle, BarChart3, Heart } from "lucide-react"

export default function Features() {
  const features = [
    {
      name: "Sybl",
      title: "Trauma-Informed AI Helper",
      description:
        "Our compassionate AI assistant understands trauma-informed care principles and helps you navigate available resources with an interactive map showing the nearest agencies that can help.",
      icon: Brain,
      color: "bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400",
      features: [
        "Interactive resource mapping",
        "Trauma-informed responses",
        "24/7 availability",
        "Personalized guidance",
      ],
    },
    {
      name: "UpSkil",
      title: "Adaptive E-Learning Platform",
      description:
        "Our intelligent learning system adapts to your pace and learning style in real-time, using data analysis and ABA principles to optimize your educational journey.",
      icon: GraduationCap,
      color: "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
      features: ["Real-time adaptation", "Personalized learning paths", "Progress tracking", "Data-driven insights"],
    },
    {
      name: "MyIkigai",
      title: "AI Career Development Suite",
      description:
        "Build professional resumes and cover letters through interactive chat, plus get personalized interview preparation to help you land your dream job.",
      icon: Target,
      color: "bg-orange-100 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400",
      features: ["AI resume builder", "Cover letter assistance", "Interview preparation", "Career guidance"],
    },
  ]

  return (
    <section id="features" className="py-20 bg-muted/30 relative overflow-hidden">
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-4">Innovative Tools for Real Results</h2>
          <p className="text-xl text-foreground max-w-3xl mx-auto">
            Our three core platforms work together to provide comprehensive support tailored to your unique needs and
            goals.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-card/50 backdrop-blur-sm border border-border hover:border-emerald-500/50"
            > 
              <CardContent className="p-8">
                <div className={`w-16 h-16 ${feature.color} rounded-2xl flex items-center justify-center mb-6`}>
                  <feature.icon className="w-8 h-8" />
                </div>

                <div className="mb-2">
                  <span className="text-sm font-semibold text-emerald-600 uppercase tracking-wide">{feature.name}</span>
                </div>

                <h3 className="text-2xl font-bold text-foreground mb-4">{feature.title}</h3>

                <p className="text-foreground mb-6 leading-relaxed">{feature.description}</p>

                <ul className="space-y-2">
                  {feature.features.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-center text-sm text-foreground">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full mr-3"></div>
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            
            </Card>
          ))}
        </div>

        <div className="mt-16 bg-card/30 backdrop-blur-sm rounded-2xl p-8 lg:p-12 border border-border  hover:border-emerald-500/50">
          <div className="grid lg:grid-cols-3 gap-8 items-center">
            <div className="lg:col-span-2">
              <h3 className="text-2xl font-bold text-foreground mb-4">Why Our Approach Works</h3>
              <p className="text-foreground mb-6">
                After over a decade each in nonprofit leadership, our board was tired of the top-down approach. We
                believe in meeting clients where they are, not where we think they should be.
              </p>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <MessageCircle className="w-5 h-5 text-emerald-500 mr-3" />
                  <span className="text-foreground">Peer-based support</span>
                </div>
                <div className="flex items-center">
                  <Heart className="w-5 h-5 text-emerald-500 mr-3" />
                  <span className="text-foreground">Trauma-informed care</span>
                </div>
                <div className="flex items-center">
                  <BarChart3 className="w-5 h-5 text-emerald-500 mr-3" />
                  <span className="text-foreground">Results-driven</span>
                </div>
                <div className="flex items-center">
                  <Target className="w-5 h-5 text-emerald-500 mr-3" />
                  <span className="text-foreground">Client-centered</span>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-emerald-500 mb-2">95%</div>
              <div className="text-foreground">Success Rate</div>
              <div className="text-sm text-foreground/70 mt-2">Based on client goal achievement</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}