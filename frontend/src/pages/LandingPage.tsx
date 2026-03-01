import { FeaturesSection } from "@/features/landing/components/FeaturesSection";
import { HeroSection } from "@/features/landing/components/HeroSection";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center">
      <HeroSection />
      <FeaturesSection />
    </div>
  );
}
