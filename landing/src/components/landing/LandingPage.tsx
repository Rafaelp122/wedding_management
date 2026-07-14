import { useState } from "react";
import { useScrollSpy } from "../../hooks/useScrollSpy";
import { ThemeProvider } from "../../contexts/ThemeContext";
import { Header } from "./Header";
import { Hero } from "./Hero";
import { Features } from "./Features";
import { Methodology } from "./Methodology";
import { Testimonials } from "./Testimonials";
import { Pricing } from "./Pricing";
import { FAQ } from "./FAQ";
import { CTABanner } from "./CTABanner";
import { Footer } from "./Footer";
import { LeadModal } from "./LeadModal";

const sectionIds = ["overview", "features", "process", "pricing", "faq"];

export function LandingPage() {
  const [leadModalOpen, setLeadModalOpen] = useState(false);
  const [leadEmail, setLeadEmail] = useState("");
  const activeSection = useScrollSpy(sectionIds);

  const handleOpenLead = (email?: string) => {
    if (email) {
      setLeadEmail(email);
    }
    setLeadModalOpen(true);
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background text-foreground relative overflow-x-hidden font-sans transition-colors duration-300">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-[20%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/5 blur-[100px] pointer-events-none"></div>

        <Header activeSection={activeSection} />

        <main>
          <Hero onOpenLead={handleOpenLead} />
          <Features />
          <Methodology onOpenLead={() => handleOpenLead()} />
          <Testimonials />
          <Pricing onOpenLead={() => handleOpenLead()} />
          <FAQ />
          <CTABanner onOpenLead={() => handleOpenLead()} />
        </main>

        <Footer />

        <LeadModal
          open={leadModalOpen}
          onOpenChange={setLeadModalOpen}
          initialEmail={leadEmail}
        />
      </div>
    </ThemeProvider>
  );
}
