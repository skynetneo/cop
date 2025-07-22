import AboutHero from "@/components/about/about-hero"
import Mission from "@/components/about/mission"
import Approach from "@/components/about/approach"
import Team from "@/components/about/team"
import Impact from "@/components/about/impact"
import Values from "@/components/about/values"
import {Navbar} from "@/components/navbar";


export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
<Navbar />
      <main>
        <AboutHero />
        <Mission />
        <Approach />
        <Values />
        <Impact />
        <Team />
      </main>

    </div>
  )
}
