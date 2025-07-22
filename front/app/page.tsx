import React from "react";
import {Navbar} from "@/components/navbar";
import HeroSection from "@/components/hero";
import FeaturesSection from "@/components/featureSection";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white antialiased">
      <Navbar />
      <main>
        {/* Home Section - corresponds to "/" */}
        <HeroSection />

        {/* Features Section - corresponds to #features */}
        <FeaturesSection />

      </main>
    </div>
  );
};

export default LandingPage;